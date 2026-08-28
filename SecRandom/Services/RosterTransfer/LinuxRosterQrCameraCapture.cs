using OpenCvSharp;

namespace SecRandom.Services.RosterTransfer;

/// <summary>
/// OpenCV desktop capture loop used when CameraView has no native provider.
/// It uses V4L2 on Linux and AVFoundation on macOS, forwarding JPEG frames in memory only.
/// </summary>
public sealed class OpenCvRosterQrCameraCapture : IRosterQrCameraCapture
{
    private static readonly TimeSpan CaptureInterval = TimeSpan.FromMilliseconds(100);
    private readonly VideoCapture? _capture;
    private readonly string _cameraApiName;
    private readonly int _cameraIndex;
    private readonly string? _initializationError;
    private CancellationTokenSource? _cancellation;
    private Task? _loop;

    public event EventHandler<string>? CameraError;

    public OpenCvRosterQrCameraCapture(VideoCaptureAPIs captureApi, string cameraApiName, int cameraIndex)
    {
        PolyfillArgumentException.ThrowIfNullOrWhiteSpace(cameraApiName, nameof(cameraApiName));
        if (cameraIndex < 0)
            throw new ArgumentOutOfRangeException(nameof(cameraIndex), cameraIndex, "Camera index must not be negative.");
        _cameraApiName = cameraApiName;
        _cameraIndex = cameraIndex;

        // Win7 降级处理：OpenCvSharp4 原生 DLL（opencv_videoio_ffmpeg4130_64.dll 等）
        // 在 Win7 上可能因缺少 API 而加载失败（DllNotFoundException / BadImageFormatException）。
        // 捕获异常后标记错误，StartAsync 时通过 CameraError 通知 UI 并返回 Started（不崩溃）。
        try
        {
            _capture = new VideoCapture(cameraIndex, captureApi);
        }
        catch (DllNotFoundException ex)
        {
            _initializationError = $"Camera native library load failed (likely Win7 incompatibility): {ex.Message}";
        }
        catch (BadImageFormatException ex)
        {
            _initializationError = $"Camera native library format mismatch: {ex.Message}";
        }
        catch (Exception ex) when (ex is not (OperationCanceledException or ArgumentOutOfRangeException))
        {
            _initializationError = $"Camera initialization failed: {ex.Message}";
        }
    }

    public Task<RosterQrCameraStartResult> StartAsync(Func<byte[], Task> onFrame, CancellationToken cancellationToken)
    {
        ArgumentNullException.ThrowIfNull(onFrame);

        if (_initializationError is not null)
        {
            RosterQrCameraDispatcher.DispatchError(CameraError, this, _initializationError);
            return Task.FromResult(RosterQrCameraStartResult.Started);
        }

        if (!_capture!.IsOpened())
            throw new InvalidOperationException($"No {_cameraApiName} camera is available at index {_cameraIndex}.");

        var cancellation = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        _cancellation = cancellation;
        _loop = Task.Run(async () =>
        {
            using var frame = new Mat();
            try
            {
                while (!cancellation.IsCancellationRequested)
                {
                    if (_capture.Read(frame) && !frame.Empty() && Cv2.ImEncode(".jpg", frame, out var jpeg))
                        await RosterQrCameraDispatcher.DispatchFrameAsync(onFrame, jpeg).ConfigureAwait(false);
                    await Task.Delay(CaptureInterval, cancellation.Token).ConfigureAwait(false);
                }
            }
            catch (OperationCanceledException) { }
            catch (Exception exception) when (!cancellation.IsCancellationRequested)
            {
                RosterQrCameraDispatcher.DispatchError(CameraError, this, exception.Message);
            }
        }, CancellationToken.None);
        return Task.FromResult(RosterQrCameraStartResult.Started);
    }

    public ValueTask DisposeAsync()
    {
        _cancellation?.Cancel();
        _cancellation?.Dispose();
        _capture?.Release();
        _capture?.Dispose();
        return ValueTask.CompletedTask;
    }
}
