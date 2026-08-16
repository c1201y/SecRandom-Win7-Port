// Polyfills for net8-only exception helpers so this vendored copy
// can compile against net6.0 (the last TFM that runs on Windows 7).
namespace System;

using System.Runtime.CompilerServices;

internal static class ThrowHelpers
{
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    public static void ThrowIfDisposed(bool condition, object? instance)
    {
        if (condition)
            throw new ObjectDisposedException(instance?.GetType().FullName);
    }

    public static void ThrowIfNegative<T>(T value, [CallerArgumentExpression("value")] string? paramName = null)
        where T : struct, IComparable<T>
    {
        if (value.CompareTo(default) < 0)
            throw new ArgumentOutOfRangeException(paramName, value, "Value must not be negative.");
    }

    public static void ThrowIfLessThan<T>(T value, T other, [CallerArgumentExpression("value")] string? paramName = null)
        where T : struct, IComparable<T>
    {
        if (value.CompareTo(other) < 0)
            throw new ArgumentOutOfRangeException(paramName, value, $"Value must be greater than or equal to {other}.");
    }

    public static void ThrowIfLessThanOrEqual<T>(T value, T other, [CallerArgumentExpression("value")] string? paramName = null)
        where T : struct, IComparable<T>
    {
        if (value.CompareTo(other) <= 0)
            throw new ArgumentOutOfRangeException(paramName, value, $"Value must be greater than {other}.");
    }

    public static void ThrowIfNullOrEmpty(string? value, [CallerArgumentExpression("value")] string? paramName = null)
    {
        if (value is null)
            throw new ArgumentNullException(paramName);
        if (value.Length == 0)
            throw new ArgumentException("The value cannot be an empty string.", paramName);
    }
}
