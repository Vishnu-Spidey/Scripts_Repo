//Script Deployment
using Renci.SshNet;
using System;
using System.Net;
using System.Threading.Tasks;
using System.Text;
class Program
{
    static async Task Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        string logFilePath = $"app_{DateTime.Now:yyyyMMdd_HHmmss}.log";

        var serversFile = "IPClist.txt";
        string remoteDeploymentPath = "/var/opt/codesys/PlcLogic/Deployment/";
        string defaultPackagePath = "/etc";
        using (var logFileStream = new FileStream(logFilePath, FileMode.Create, FileAccess.Write, FileShare.ReadWrite))
        using (var logFileWriter = new StreamWriter(logFileStream) { AutoFlush = true })
        {
            var multiWriter = new MultiTextWriter(Console.Out, logFileWriter);
            Console.SetOut(multiWriter);
            Console.Write("Enter SSH username: ");
            string username = Console.ReadLine();

            Console.Write("Enter SSH password: ");
            string password = ReadPassword();

            if (!File.Exists(serversFile))
            {
                Console.WriteLine($"❌ Could not find {serversFile}");
                return;
            }

            var servers = File.ReadAllLines(serversFile)
                .Select(line => line.Trim())
                .Where(line => IPAddress.TryParse(line, out _))
                .ToList();

            Console.WriteLine($"📄 Loaded {servers.Count} IPC(s)system");



            var tasks = servers.Select(ip =>
                Task.Run(() => DeployToServer(ip, username, password, defaultPackagePath, remoteDeploymentPath))
            ).ToList();

            await Task.WhenAll(tasks);

            Console.WriteLine("\n✅ Parallel script execution completed.");

            Console.WriteLine("Press Enter to exit...");
            Console.ReadLine();
        }
        
    }
    static string ReadPassword()
    {
        string password = "";
        ConsoleKeyInfo key;

        do
        {
            key = Console.ReadKey(true);
            if (key.Key == ConsoleKey.Backspace && password.Length > 0)
            {
                password = password[0..^1];
                Console.Write("\b \b");
            }
            else if (!char.IsControl(key.KeyChar))
            {
                password += key.KeyChar;
                Console.Write("*");
            }
        } while (key.Key != ConsoleKey.Enter);

        Console.WriteLine();
        return password;
    }


    static void DeployToServer(string ip, string username, string password, string pPath, string rDeploymentPath)
    {
        Console.WriteLine($"\n🔄 Connecting to {ip}...");

        if (!TestSshConnection(ip, username, password))
        {
            Console.WriteLine($"❌ Cannot connect to {ip}. Skipping.");
            return;
        }

        try
        {

            RunRemoteScript(ip, username, password, rDeploymentPath);

            Console.WriteLine($"✅ Done on {ip}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Error on {ip}: {ex.Message}");
        }
    }
    static bool TestSshConnection(string ip, string username, string password)
    {
        using var ssh = new SshClient(ip, username, password);
        try
        {
            ssh.Connect();
            if (ssh.IsConnected)
            {
                ssh.Disconnect();
                return true;
            }
        }
        catch (Exception) { }
        return false;
    }


    static void RunRemoteScript(string ip, string username, string password, string rDeploymentPath)
    {
        using var ssh = new SshClient(ip, username, password);
        ssh.Connect();
        string command = $"echo \"{password}\" | sudo -S mkdir -p /etc/samba && echo \"{password}\" | sudo -S bash -c 'echo -e \"username={username}\\npassword={password}\" > /etc/samba/ScadaServerCredentials' && echo \"{password}\" | sudo -S chmod 600 /etc/samba/ScadaServerCredentials && echo \"{password}\" | sudo -S mkdir -p /mnt/sharedVTSCADA && echo '//10.0.0.41/FilesPrep  /mnt/sharedVTSCADA  cifs  credentials=/etc/samba/ScadaServerCredentials,iocharset=utf8,uid=1000,gid=1000  0  0' | sudo -S tee -a /etc/fstab > /dev/null && echo \"{password}\" | sudo -S systemctl daemon-reload";
        var result = ssh.RunCommand(command);
        ssh.Disconnect();

        if (!string.IsNullOrWhiteSpace(result.Result))
            Console.WriteLine($"📥 Output from {ip}:\n{result.Result}");

        if (!string.IsNullOrWhiteSpace(result.Error))
            Console.WriteLine($"⚠️ Error/Warning from {ip}:\n{result.Error}");
    }
    class MultiTextWriter : TextWriter
    {
        private readonly TextWriter[] writers;
        public MultiTextWriter(params TextWriter[] writers)
        {
            this.writers = writers;
        }

        public override Encoding Encoding => Encoding.UTF8;

        public override void Write(char value)
        {
            foreach (var writer in writers)
                writer.Write(value);
        }

        public override void WriteLine(string value)
        {
            foreach (var writer in writers)
                writer.WriteLine(value);
        }

        public override void Flush()
        {
            foreach (var writer in writers)
                writer.Flush();
        }
    }


}
