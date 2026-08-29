using System;
using System.IO;
using System.Linq;
using SecRandom.Core.Models.Linkage;
using SecRandom.Services.Linkage;

namespace SecRandom.Core.Tests;

public sealed class ProbeCsesTests
{
    [Fact]
    public void Probe_ParseUserFile()
    {
        var parser = new CsesScheduleParser();
        var path = Path.Combine(Path.GetTempPath(), "opencode", "906课表.yml");
        var content = File.ReadAllText(path);
        InvalidDataException caught;
        try
        {
            var schedule = parser.Parse(content);
            caught = null!;
            Assert.Fail($"OK: periods={schedule.PeriodCount}");
        }
        catch (InvalidDataException ex)
        {
            caught = ex;
        }

        var day = caught.Data["Argument"];
        Assert.Fail($"ERR={caught.Data["CsesScheduleError"]} arg={day} msg={caught.Message}");
    }
}