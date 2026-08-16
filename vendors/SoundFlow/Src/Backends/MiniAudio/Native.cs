using System.Reflection;
using System.Runtime.InteropServices;
using SoundFlow.Backends.MiniAudio.Enums;
using SoundFlow.Enums;

namespace SoundFlow.Backends.MiniAudio;

internal static unsafe partial class Native
{
    private const string LibraryName = "miniaudio";
    
    #region Delegates
    
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
    public delegate void AudioCallback(nint device, nint output, nint input, uint length);

    [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
    public delegate Result BufferProcessingCallback(
        nint pCodecContext,          // The native decoder/encoder instance pointer (ma_decoder*, ma_encoder*)
        nint pBuffer,                // The buffer pointer (void* pBufferOut or const void* pBufferIn)
        nuint bytesRequested,        // The number of bytes requested (bytesToRead or bytesToWrite)
        out nuint bytesTransferred   // The actual number of bytes processed/transferred (size_t*)
    );

    [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
    public delegate Result SeekCallback(nint pDecoder, long byteOffset, SeekPoint origin);
    
    #endregion
    
    #region Initialization
    
    static Native()
    {
        NativeLibrary.SetDllImportResolver(typeof(Native).Assembly, NativeLibraryResolver.Resolve);
    }

    private static class NativeLibraryResolver
    {
        public static nint Resolve(string libraryName, Assembly assembly, DllImportSearchPath? searchPath)
        {
            // 1. Get the platform-specific library file name (e.g., "libminiaudio.so", "miniaudio.dll").
            var platformSpecificName = GetPlatformSpecificLibraryName(libraryName);

            // 2. Try to load the library using its platform-specific name, allowing OS to find it in standard paths.
            if (NativeLibrary.TryLoad(platformSpecificName, assembly, searchPath, out var library))
                return library;

            // 3. If that fails, try to load it from the application's 'runtimes' directory for self-contained apps.
            var relativePath = GetLibraryPath(libraryName); // This still gives the full relative path
            var fullPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, relativePath);

            if (File.Exists(fullPath) && NativeLibrary.TryLoad(fullPath, out library))
                return library;
            
            // 4. If not found, use Load() to let the runtime throw a detailed DllNotFoundException.
            return NativeLibrary.Load(fullPath); 
        }

        /// <summary>
        /// Gets the platform-specific library name
        /// </summary>
        private static string GetPlatformSpecificLibraryName(string libraryName)
        {
            if (OperatingSystem.IsWindows())
                return $"{libraryName}.dll";

            if (OperatingSystem.IsMacOS())
                return $"lib{libraryName}.dylib";
            
            // For iOS frameworks, the binary has the same name as the framework
            if (OperatingSystem.IsIOS())
                return libraryName;

            // Default to Linux/Android/FreeBSD convention
            return $"lib{libraryName}.so";
        }

        /// <summary>
        /// Constructs the relative path to the native library within the 'runtimes' folder.
        /// </summary>
        private static string GetLibraryPath(string libraryName)
        {
            const string relativeBase = "runtimes";
            var platformSpecificName = GetPlatformSpecificLibraryName(libraryName);

            string rid;
            if (OperatingSystem.IsWindows())
            {
                rid = RuntimeInformation.ProcessArchitecture switch
                {
                    Architecture.X86 => "win-x86",
                    Architecture.X64 => "win-x64",
                    Architecture.Arm64 => "win-arm64",
                    _ => throw new PlatformNotSupportedException(
                        $"Unsupported Windows architecture: {RuntimeInformation.ProcessArchitecture}")
                };
            }
            else if (OperatingSystem.IsMacOS())
            {
                rid = RuntimeInformation.ProcessArchitecture switch
                {
                    Architecture.X64 => "osx-x64",
                    Architecture.Arm64 => "osx-arm64",
                    _ => throw new PlatformNotSupportedException(
                        $"Unsupported macOS architecture: {RuntimeInformation.ProcessArchitecture}")
                };
            }
            else if (OperatingSystem.IsLinux())
            {
                rid = RuntimeInformation.ProcessArchitecture switch
                {
                    Architecture.X64 => "linux-x64",
                    Architecture.Arm => "linux-arm",
                    Architecture.Arm64 => "linux-arm64",
                    _ => throw new PlatformNotSupportedException(
                        $"Unsupported Linux architecture: {RuntimeInformation.ProcessArchitecture}")
                };
            }
            else if (OperatingSystem.IsAndroid())
            {
                 rid = RuntimeInformation.ProcessArchitecture switch
                {
                    Architecture.X64 => "android-x64",
                    Architecture.Arm => "android-arm",
                    Architecture.Arm64 => "android-arm64",
                    _ => throw new PlatformNotSupportedException(
                        $"Unsupported Android architecture: {RuntimeInformation.ProcessArchitecture}")
                };
            }
            else if (OperatingSystem.IsIOS())
            {
                rid = RuntimeInformation.ProcessArchitecture switch
                {
                    // iOS uses .framework folders
                    Architecture.Arm64 => "ios-arm64",
                    _ => throw new PlatformNotSupportedException(
                        $"Unsupported iOS architecture: {RuntimeInformation.ProcessArchitecture}")
                };
                return Path.Combine(relativeBase, rid, "native", $"{libraryName}.framework", platformSpecificName);
            }
            else if (OperatingSystem.IsFreeBSD())
            {
                rid = RuntimeInformation.ProcessArchitecture switch
                {
                    Architecture.X64 => "freebsd-x64",
                    Architecture.Arm64 => "freebsd-arm64",
                    _ => throw new PlatformNotSupportedException(
                        $"Unsupported FreeBSD architecture: {RuntimeInformation.ProcessArchitecture}")
                };
            }
            else
            {
                throw new PlatformNotSupportedException(
                    $"Unsupported operating system: {RuntimeInformation.OSDescription}");
            }

            return Path.Combine(relativeBase, rid, "native", platformSpecificName);
        }
    }
    
    #endregion
    
    #region Encoder

    [DllImport(LibraryName, EntryPoint = "ma_encoder_init")]
    public static extern Result EncoderInit(BufferProcessingCallback onRead, SeekCallback onSeekCallback, nint pUserData, nint pConfig, nint pEncoder);

    [DllImport(LibraryName, EntryPoint = "ma_encoder_uninit")]
    public static extern void EncoderUninit(nint pEncoder);

    [DllImport(LibraryName, EntryPoint = "ma_encoder_write_pcm_frames")]
    public static extern Result EncoderWritePcmFrames(nint pEncoder, nint pFramesIn, ulong frameCount,
        ulong* pFramesWritten);

    #endregion

    #region Decoder

    [DllImport(LibraryName, EntryPoint = "ma_decoder_init")]
    public static extern Result DecoderInit(BufferProcessingCallback onRead, SeekCallback onSeekCallback, nint pUserData,
        nint pConfig, nint pDecoder);

    [DllImport(LibraryName, EntryPoint = "ma_decoder_uninit")]
    public static extern Result DecoderUninit(nint pDecoder);

    [DllImport(LibraryName, EntryPoint = "ma_decoder_read_pcm_frames")]
    public static extern Result DecoderReadPcmFrames(nint decoder, nint framesOut, ulong frameCount,
        out ulong framesRead);

    [DllImport(LibraryName, EntryPoint = "ma_decoder_seek_to_pcm_frame")]
    public static extern Result DecoderSeekToPcmFrame(nint decoder, ulong frame);

    [DllImport(LibraryName, EntryPoint = "ma_decoder_get_length_in_pcm_frames")]
    public static extern Result DecoderGetLengthInPcmFrames(nint decoder, out ulong length);

    #endregion

    #region Context

    [DllImport(LibraryName, EntryPoint = "ma_context_init")]
    public static extern Result ContextInit(nint backends, uint backendCount, nint config, nint context);
    
    [DllImport(LibraryName, EntryPoint = "ma_context_uninit")]
    public static extern void ContextUninit(nint context);

    #endregion

    #region Device

    [DllImport(LibraryName, EntryPoint = "sf_get_devices")]
    public static extern Result GetDevices(nint context, out nint pPlaybackDevices, out nint pCaptureDevices, out nint playbackDeviceCount, out nint captureDeviceCount);

    [DllImport(LibraryName, EntryPoint = "ma_device_init")]
    public static extern Result DeviceInit(nint context, nint config, nint device);

    [DllImport(LibraryName, EntryPoint = "ma_device_uninit")]
    public static extern void DeviceUninit(nint device);

    [DllImport(LibraryName, EntryPoint = "ma_device_start")]
    public static extern Result DeviceStart(nint device);

    [DllImport(LibraryName, EntryPoint = "ma_device_stop")]
    public static extern Result DeviceStop(nint device);

    #endregion

    #region Allocations

    [DllImport(LibraryName, EntryPoint = "sf_allocate_encoder")]
    public static extern nint AllocateEncoder();

    [DllImport(LibraryName, EntryPoint = "sf_allocate_decoder")]
    public static extern nint AllocateDecoder();

    [DllImport(LibraryName, EntryPoint = "sf_allocate_context")]
    public static extern nint AllocateContext();

    [DllImport(LibraryName, EntryPoint = "sf_allocate_device")]
    public static extern nint AllocateDevice();

    [DllImport(LibraryName, EntryPoint = "sf_allocate_decoder_config")]
    public static extern nint AllocateDecoderConfig(SampleFormat format, uint channels, uint sampleRate);

    [DllImport(LibraryName, EntryPoint = "sf_allocate_encoder_config")]
    public static extern nint AllocateEncoderConfig(EncodingFormat encodingFormat, SampleFormat format, uint channels,
        uint sampleRate);

    [DllImport(LibraryName, EntryPoint = "sf_allocate_device_config")]
    public static extern nint AllocateDeviceConfig(Capability capabilityType, uint sampleRate, AudioCallback dataCallback, nint pSfConfig);

    #endregion

    #region Utils

    [DllImport(LibraryName, EntryPoint = "sf_free")]
    public static extern void Free(nint ptr);
    
    [DllImport(LibraryName, EntryPoint = "sf_free_device_infos")]
    public static extern void FreeDeviceInfos(nint deviceInfos, uint count);

    #endregion
}
