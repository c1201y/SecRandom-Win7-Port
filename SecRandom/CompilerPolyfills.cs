namespace System.Runtime.CompilerServices;

// net6 缺少 C# 11 required 成员所需的编译器特性;本程序集内自备一份,
// 编译器优先使用当前程序集的定义。
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
