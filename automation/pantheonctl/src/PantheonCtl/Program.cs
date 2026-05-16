namespace PantheonCtl;

internal static class Program
{
    private static readonly string[] PlannedCommands =
    [
        "docs validate",
        "links check",
        "systems list",
        "devices list",
        "services list",
        "inventory generate",
        "automation classify",
        "ansible render-inventory",
        "pulumi render-config",
        "report readiness"
    ];

    private static int Main(string[] args)
    {
        Console.WriteLine("pantheonctl status: scaffold");
        Console.WriteLine("Read-only and generate-only commands are planned.");
        Console.WriteLine();
        Console.WriteLine("Planned commands:");

        foreach (var command in PlannedCommands)
        {
            Console.WriteLine($"  pantheonctl {command}");
        }

        if (args.Length > 0)
        {
            Console.WriteLine();
            Console.WriteLine("Command execution is deferred until validation behavior is implemented.");
        }

        return 0;
    }
}
