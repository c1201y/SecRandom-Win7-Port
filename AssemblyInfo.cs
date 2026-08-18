using System.Reflection;
using SecRandom;

[assembly: AssemblyVersion("3.0.0.0")]
[assembly: AssemblyInformationalVersion("3.0.0.0+移植版")]
[assembly: AssemblyTitle("SecRandom")]
[assembly: AssemblyProduct("SecRandom")]

#if NETCOREAPP
// [assembly: SupportedOSPlatform("Windows")]
#endif
#if Platforms_MacOs
[assembly:SupportedOSPlatform("macos")]
#endif