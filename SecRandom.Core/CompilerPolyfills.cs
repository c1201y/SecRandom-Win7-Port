// Polyfill for C# 12 RequiredMemberAttribute and CompilerFeatureRequiredAttribute
// so that net6.0 projects can use required members with LangVersion latest.
namespace System.Runtime.CompilerServices
{
    [AttributeUsage(AttributeTargets.Class | AttributeTargets.Struct | AttributeTargets.Method, Inherited = false)]
    internal sealed class RequiredMemberAttribute : Attribute
    {
    }

    [AttributeUsage(AttributeTargets.All, Inherited = false)]
    internal sealed class CompilerFeatureRequiredAttribute : Attribute
    {
        public CompilerFeatureRequiredAttribute(string featureName)
        {
            FeatureName = featureName;
        }

        public string FeatureName { get; }
    }

    // Polyfill for C# 12 UnsafeAccessorAttribute
    [AttributeUsage(AttributeTargets.Field | AttributeTargets.Property | AttributeTargets.Method, Inherited = false)]
    internal sealed class UnsafeAccessorAttribute : Attribute
    {
        public UnsafeAccessorAttribute(UnsafeAccessorKind kind)
        {
            Kind = kind;
        }

        public UnsafeAccessorKind Kind { get; }
    }

    internal enum UnsafeAccessorKind
    {
        Field,
        Property,
        Method
    }
}

// Polyfill for .NET 6 ArgumentException.ThrowIfNullOrWhiteSpace
namespace System
{
    public static class PolyfillArgumentException
    {
        public static void ThrowIfNullOrWhiteSpace(string? argument, string? paramName)
        {
            if (string.IsNullOrWhiteSpace(argument))
            {
                throw new ArgumentNullException(paramName);
            }
        }
    }
}