using System;

namespace SecRandom.Services.Draw;

// Pitch-preserving time-stretch for short clips such as voice announcements.
// SOLA overlap-add with a bounded similarity search keeps speech intelligible
// without a native DSP dependency; processing runs fully offline before the
// clip is handed to waveOut as one continuous PCM stream.
internal static class AudioTempoStretch
{
    private const int FrameMilliseconds = 40;
    private const int SearchMilliseconds = 5;

    public static bool TryStretch(
        float[] interleavedSamples,
        int channels,
        int sampleRate,
        double speed,
        out float[] stretched,
        out int stretchedFrameCount)
    {
        stretched = interleavedSamples;
        stretchedFrameCount = interleavedSamples.Length / Math.Max(1, channels);

        var factor = Math.Clamp(speed, 0.25, 4);
        if (channels is < 1 or > 2 || sampleRate <= 0 || interleavedSamples.Length % channels != 0)
            return false;

        var frameCount = interleavedSamples.Length / channels;
        if (Math.Abs(factor - 1d) < 0.001 || frameCount < 2)
            return true;

        var frameLength = Math.Max(256, sampleRate * FrameMilliseconds / 1000);
        var synthesisHop = frameLength / 2;
        var analysisHop = Math.Max(1, (int)Math.Round(synthesisHop / factor));
        var searchRadius = sampleRate * SearchMilliseconds / 1000;
        if (synthesisHop < 1 || frameCount <= frameLength)
            return true;

        var channelData = new float[channels][];
        for (var channel = 0; channel < channels; channel++)
        {
            channelData[channel] = new float[frameCount];
            for (var i = 0; i < frameCount; i++)
                channelData[channel][i] = interleavedSamples[(i * channels) + channel];
        }

        var capacity = (int)(frameCount / factor) + (frameLength * 2) + synthesisHop;
        var outputChannels = new float[channels][];
        for (var channel = 0; channel < channels; channel++)
            outputChannels[channel] = new float[capacity];

        var seedLength = Math.Min(frameLength, frameCount);
        for (var channel = 0; channel < channels; channel++)
            Array.Copy(channelData[channel], outputChannels[channel], seedLength);

        var reference = outputChannels[0];
        var input = channelData[0];
        var inputPosition = analysisHop;
        var outputPosition = synthesisHop;

        while (inputPosition + frameLength <= frameCount && outputPosition + frameLength <= capacity)
        {
            var lowerBound = Math.Max(-searchRadius, -inputPosition);
            var upperBound = Math.Min(searchRadius, frameCount - (inputPosition + frameLength));
            var delta = 0;
            if (upperBound >= lowerBound)
                delta = FindAlignment(input, reference, inputPosition, outputPosition, synthesisHop, lowerBound, upperBound);

            var sourcePosition = inputPosition + delta;
            for (var channel = 0; channel < channels; channel++)
            {
                var source = channelData[channel];
                var destination = outputChannels[channel];
                for (var i = 0; i < frameLength; i++)
                {
                    if (i < synthesisHop)
                    {
                        var blend = i / (float)synthesisHop;
                        destination[outputPosition + i] =
                            (destination[outputPosition + i] * (1f - blend)) + (source[sourcePosition + i] * blend);
                    }
                    else
                    {
                        destination[outputPosition + i] = source[sourcePosition + i];
                    }
                }
            }

            outputPosition += synthesisHop;
            inputPosition += analysisHop;
        }

        stretchedFrameCount = Math.Min(outputPosition + synthesisHop, capacity);
        stretched = new float[stretchedFrameCount * channels];
        for (var i = 0; i < stretchedFrameCount; i++)
        {
            for (var channel = 0; channel < channels; channel++)
                stretched[(i * channels) + channel] = outputChannels[channel][i];
        }

        return true;
    }

    // Align the incoming frame tail with the already-written output tail by
    // maximizing the normalized cross-correlation over the overlap region.
    private static int FindAlignment(
        float[] input,
        float[] reference,
        int inputPosition,
        int outputPosition,
        int correlationLength,
        int lowerBound,
        int upperBound)
    {
        var bestDelta = 0;
        var bestScore = double.NegativeInfinity;
        for (var delta = lowerBound; delta <= upperBound; delta++)
        {
            var position = inputPosition + delta;
            double dot = 0;
            double energy = 1e-9;
            for (var i = 0; i < correlationLength; i++)
            {
                var value = input[position + i];
                dot += reference[outputPosition + i] * value;
                energy += value * value;
            }

            var score = dot / Math.Sqrt(energy);
            if (score > bestScore)
            {
                bestScore = score;
                bestDelta = delta;
            }
        }

        return bestDelta;
    }
}
