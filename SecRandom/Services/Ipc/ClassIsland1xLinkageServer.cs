using System;
using System.IO;
using System.IO.Pipes;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using SecRandom.Core.Services.Ipc;
using SecRandom.Shared.Models.Ipc;

namespace SecRandom.Services.Ipc;

/// <summary>
///     ClassIsland 1.x linkage pipe: the ConvenientText plugin sends secrandom:// URL
///     commands as JSON lines over the <c>SecRandom.secrandom</c> pipe and expects a JSON
///     response line. Commands are validated and routed exactly like the built-in IPC pipe.
/// </summary>
public sealed class ClassIsland1xLinkageServer(
    ILogger<ClassIsland1xLinkageServer> logger,
    Func<IpcRequestEnvelope, CancellationToken, Task<IpcResponseEnvelope>> requestHandler) : BackgroundService
{
    public const string PipeName = "SecRandom.secrandom";
    private static readonly TimeSpan FrameReadTimeout = TimeSpan.FromSeconds(5);
    private const int MaxConcurrentConnections = 8;
    private static readonly UTF8Encoding StrictUtf8 = new(false, true);
    private static readonly JsonSerializerOptions IpcJsonOptions = new(JsonSerializerDefaults.Web);
    private readonly SemaphoreSlim _connectionGate = new(MaxConcurrentConnections, MaxConcurrentConnections);

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            var gateEntered = false;
            NamedPipeServerStream? server = null;
            try
            {
                await _connectionGate.WaitAsync(stoppingToken).ConfigureAwait(false);
                gateEntered = true;
                server = new NamedPipeServerStream(
                    PipeName,
                    PipeDirection.InOut,
                    maxNumberOfServerInstances: MaxConcurrentConnections,
                    PipeTransmissionMode.Byte,
                    PipeOptions.Asynchronous | PipeOptions.CurrentUserOnly);

                await server.WaitForConnectionAsync(stoppingToken).ConfigureAwait(false);
                var acceptedServer = server;
                _ = Task.Run(() => HandleAcceptedConnectionAsync(acceptedServer, stoppingToken), CancellationToken.None);
                server = null;
                gateEntered = false;
            }
            catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
            {
                server?.Dispose();
                if (gateEntered)
                    _connectionGate.Release();
                break;
            }
            catch
            {
                server?.Dispose();
                if (gateEntered)
                    _connectionGate.Release();
                // 连接中断或管道错误，短暂等待后继续监听
                await Task.Delay(100, stoppingToken).ConfigureAwait(false);
            }
        }
    }

    private async Task HandleAcceptedConnectionAsync(NamedPipeServerStream server, CancellationToken cancellationToken)
    {
        await using var connection = server;
        try
        {
            await HandleConnectionAsync(connection, cancellationToken).ConfigureAwait(false);
        }
        catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested)
        {
        }
        catch (Exception exception)
        {
            logger.LogDebug(exception, "ClassIsland 1.x linkage pipe request failed.");
        }
        finally
        {
            _connectionGate.Release();
        }
    }

    private static async Task<string?> ReadRequestLineAsync(StreamReader reader, CancellationToken cancellationToken)
    {
        var buffer = new char[ProtocolRequestParser.MaxRequestLength + 1];
        var length = 0;
        while (length < buffer.Length)
        {
            var character = await reader.ReadAsync(buffer.AsMemory(length, 1), cancellationToken).ConfigureAwait(false);
            if (character == 0)
                break;
            if (buffer[length] == '\n')
                break;
            length++;
        }

        return length > ProtocolRequestParser.MaxRequestLength ? null : new string(buffer, 0, length).TrimEnd('\r');
    }

    private async Task HandleConnectionAsync(NamedPipeServerStream server, CancellationToken cancellationToken)
    {
        using var reader = new StreamReader(server, StrictUtf8, detectEncodingFromByteOrderMarks: false, leaveOpen: true);
        await using var writer = new StreamWriter(server, StrictUtf8, leaveOpen: true);
        using var frameCts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        frameCts.CancelAfter(FrameReadTimeout);

        string? frame;
        try
        {
            frame = await ReadRequestLineAsync(reader, frameCts.Token).ConfigureAwait(false);
        }
        catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
        {
            return;
        }

        if (string.IsNullOrWhiteSpace(frame) || frame[0] != '{')
            return;

        IpcRequestEnvelope? request;
        try
        {
            request = JsonSerializer.Deserialize<IpcRequestEnvelope>(frame, IpcJsonOptions);
        }
        catch (JsonException)
        {
            return;
        }

        if (request is null || request.Version is not (0 or 1)
            || !string.Equals(request.Type, "url", StringComparison.OrdinalIgnoreCase)
            || string.IsNullOrWhiteSpace(request.Payload?.Url))
            return;

        IpcResponseEnvelope response;
        try
        {
            response = await requestHandler(request, cancellationToken).ConfigureAwait(false);
        }
        catch
        {
            response = IpcResponseEnvelope.TransportFailure(request.Type, "internal_error", "IPC 请求处理失败。");
        }

        await writer.WriteLineAsync(JsonSerializer.Serialize(response, IpcJsonOptions)).ConfigureAwait(false);
        await writer.FlushAsync().ConfigureAwait(false);
    }
}