using Microsoft.AspNetCore.Hosting;

namespace LinkAggregatorBot
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var host = new WebHostBuilder()
                .UseUrls("http://*:8080")
                .UseEnvironment(EnvironmentName.Production)
                .UseKestrel()
                .UseStartup<Startup>()
                .Build();

            host.Run();
        }
    }
}
