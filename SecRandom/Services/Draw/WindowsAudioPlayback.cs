using System;
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
    public static async Task PlayToCompletionAsync(string path, int volume, CancellationToken cancellationToken = default)
    {
        using var session = Start(path, Math.Clamp(volume, 0, 100) / 100f, false);
        var completion = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        session.PlaybackEnded += (_, _) => completion.TrySetResult();
        using var registration = cancellationToken.Register(() => completion.TrySetCanceled(cancellationToken));
        session.Play();
        await completion.Task.ConfigureAwait(false);
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
