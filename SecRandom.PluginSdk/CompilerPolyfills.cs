namespace System.Runtime.CompilerServices;

// net6 缺少 C# 11 required 成员所需的编译器特性;PluginSdk 程序集内自备一份。
[AttributeUsage(AttributeTargets.All, AllowMultiple = false, Inherited = false)]
internal sealed class RequiredMemberAttribute : Attribute
{
}

[AttributeUsage(AttributeTargets.All, AllowMultiple = false, Inherited = false)]
internal sealed class CompilerFeatureRequiredAttribute : Attribute
{
    public CompilerFeatureRequiredAttribute(string featureName)
    {
        FeatureName = featureName;
    }

    public string FeatureName { get; }
}
