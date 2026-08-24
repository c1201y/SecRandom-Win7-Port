using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using NAudio.Wave;
using NLayer.NAudioSupport;

namespace SecRandom.Services.Draw;

// Decode MP3 with NLayer and send PCM through the Windows waveOut API. This keeps
// playback inside the app without WMP, COM, MiniAudio, or a bundled native codec.
internal static class WindowsAudioPlayback
{
    public static async Task PlayToCompletionAsync(
        string path,
        int volume,
        int playbackSpeed = 100,
        CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        var clampedVolume = Math.Clamp(volume, 0, 100) / 100f;
        var speed = Math.Clamp(playbackSpeed, 1, 200) / 100f;
        if (Math.Abs(speed - 1d) < 0.01)
        {
            using var session = Start(path, clampedVolume, false);
            var completion = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
            session.PlaybackEnded += (_, _) => completion.TrySetResult();
            using var registration = cancellationToken.Register(() => completion.TrySetCanceled(cancellationToken));
            session.Play();
            await completion.Task.ConfigureAwait(false);
            return;
        }

        await PlayStretchedAsync(path, clampedVolume, speed, cancellationToken).ConfigureAwait(false);
    }

    // Voice clips are short, so the tempo-adjusted variant decodes fully and
    // stretches offline; waveOut then plays one continuous PCM stream.
    private static async Task PlayStretchedAsync(
        string path,
        float volume,
        double speed,
        CancellationToken cancellationToken)
    {
        RawSourceWaveStream stretchedStream;
        using (var source = OpenSource(path))
        {
            if (source.TotalTime > TimeSpan.FromMinutes(10))
            {
                await PlayToCompletionAsync(path, (int)Math.Round(volume * 100), 100, cancellationToken)
                    .ConfigureAwait(false);
                return;
            }

            var sampleProvider = source.ToSampleProvider();
            var format = sampleProvider.WaveFormat;
            var samples = DecodeSamples(sampleProvider);
            if (!AudioTempoStretch.TryStretch(samples, format.Channels, format.SampleRate, speed, out var stretched, out _))
            {
                await PlayToCompletionAsync(path, (int)Math.Round(volume * 100), 100, cancellationToken)
                    .ConfigureAwait(false);
                return;
            }

            stretchedStream = new RawSourceWaveStream(
                new MemoryStream(EncodePcm16(stretched)),
                new WaveFormat(format.SampleRate, format.Channels));
        }

        try
        {
            var output = new WaveOutEvent
            {
                DesiredLatency = 150,
                NumberOfBuffers = 3
            };
            try
            {
                var completion = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
                output.PlaybackStopped += (_, _) => completion.TrySetResult();
                using var registration = cancellationToken.Register(() => completion.TrySetCanceled(cancellationToken));
                output.Volume = volume;
                output.Init(stretchedStream);
                output.Play();
                await completion.Task.ConfigureAwait(false);
            }
            finally
            {
                output.Dispose();
            }
        }
        finally
        {
            stretchedStream.Dispose();
        }
    }

    private static WaveStream OpenSource(string path) =>
        Path.GetExtension(path).Equals(".mp3", StringComparison.OrdinalIgnoreCase)
            ? new ManagedMpegStream(path)
            : new WaveFileReader(path);

    private static float[] DecodeSamples(ISampleProvider sampleProvider)
    {
        List<float[]> chunks = [];
        long totalSamples = 0;
        var buffer = new float[Math.Max(sampleProvider.WaveFormat.SampleRate, 8000) * sampleProvider.WaveFormat.Channels];
        int read;
        while ((read = sampleProvider.Read(buffer, 0, buffer.Length)) > 0)
        {
            var chunk = new float[read];
            Array.Copy(buffer, chunk, read);
            chunks.Add(chunk);
            totalSamples += read;
        }

        var result = new float[totalSamples];
        var offset = 0;
        foreach (var chunk in chunks)
        {
            Array.Copy(chunk, 0, result, offset, chunk.Length);
            offset += chunk.Length;
        }

        return result;
    }

    private static byte[] EncodePcm16(float[] samples)
    {
        var pcm = new short[samples.Length];
        for (var i = 0; i < samples.Length; i++)
            pcm[i] = (short)(Math.Clamp(samples[i], -1f, 1f) * 32767f);

        var bytes = new byte[pcm.Length * sizeof(short)];
        Buffer.BlockCopy(pcm, 0, bytes, 0, bytes.Length);
        return bytes;
    }

    public static Session Start(string path, float volume, bool loop) => new(path, volume, loop);

    internal sealed class Session : IDisposable
    {
        private readonly WaveStream _source;
        private readonly WaveOutEvent _output;
        private readonly bool _loop;
        private int _disposed;
        private bool _playing;

        public Session(string path, float volume, bool loop)
        {
            if (!OperatingSystem.IsWindows())
                throw new PlatformNotSupportedException("Windows audio is only available on Windows.");
            if (!File.Exists(path))
                throw new FileNotFoundException("Audio file was not found.", path);

            _source = Path.GetExtension(path).Equals(".mp3", StringComparison.OrdinalIgnoreCase)
                ? new ManagedMpegStream(path)
                : new WaveFileReader(path);
            _output = new WaveOutEvent
            {
                DesiredLatency = 150,
                NumberOfBuffers = 3
            };
            _output.Init(_source);
            _output.Volume = Math.Clamp(volume, 0, 1);
            _output.PlaybackStopped += OnPlaybackStopped;
            _loop = loop;
        }

        public event EventHandler<EventArgs>? PlaybackEnded;

        public float DurationSeconds => (float)_source.TotalTime.TotalSeconds;

        public float Volume
        {
            get => _output.Volume;
            set => _output.Volume = Math.Clamp(value, 0, 1);
        }

        public void Play()
        {
            ThrowIfDisposed();
            _playing = true;
            _output.Play();
        }

        public void Stop()
        {
            if (Volatile.Read(ref _disposed) != 0)
                return;

            _playing = false;
            _output.Stop();
        }

        public void Dispose()
        {
            if (Interlocked.Exchange(ref _disposed, 1) != 0)
                return;

            _playing = false;
            _output.PlaybackStopped -= OnPlaybackStopped;
            _output.Stop();
            _output.Dispose();
            _source.Dispose();
        }

        private void OnPlaybackStopped(object? sender, StoppedEventArgs e)
        {
            if (Volatile.Read(ref _disposed) != 0 || !_playing)
                return;

            if (_loop)
            {
                _source.Position = 0;
                _output.Play();
                return;
            }

            _playing = false;
            PlaybackEnded?.Invoke(this, EventArgs.Empty);
        }

        private void ThrowIfDisposed()
        {
            if (Volatile.Read(ref _disposed) != 0)
                throw new ObjectDisposedException(nameof(Session));
        }
    }
}
