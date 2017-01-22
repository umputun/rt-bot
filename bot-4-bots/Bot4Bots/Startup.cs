using System;
using System.IO;
using System.Threading.Tasks;
using Bot4Bots.Github;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace Bot4Bots
{
    public static class ConfigurationKeys
    {
        public const string APP_TARGET_USER = "APP_TARGET_USER";
        public const string APP_TARGET_REPO = "APP_TARGET_REPO";
        public const string APP_DATA_REFRESH_SECONDS = "APP_DATA_REFRESH_SECONDS";
    }

    public class Startup
    {
        public static void Main(string[] args)
        {
            var host = new WebHostBuilder()
                .UseUrls("http://0.0.0.0:8080")
                .UseKestrel()
                .UseContentRoot(Directory.GetCurrentDirectory())
                .UseStartup<Startup>()
                .Build();

            RunPreloadTask(
                host.Services.GetService<GithubService>(),
                host.Services.GetService<IConfiguration>());

            host.Run();
        }

        private static void RunPreloadTask(GithubService githubService, IConfiguration configuration)
        {
            githubService.LoadSummaries();

            //refreshing data in background
            Task.Run(async () =>
            {
                do
                {
                    var delay = TimeSpan.FromSeconds(
                        configuration.GetValue<int>(ConfigurationKeys.APP_DATA_REFRESH_SECONDS));

                    await Task.Delay(delay);

                    githubService.LoadSummaries();
                } while (true);
                // ReSharper disable once FunctionNeverReturns
            });
        }
        
        public Startup(IHostingEnvironment env)
        {
            var builder = new ConfigurationBuilder()
                .SetBasePath(env.ContentRootPath)
                .AddJsonFile("appsettings.json", optional: true, reloadOnChange: true)
                .AddJsonFile($"appsettings.{env.EnvironmentName}.json", optional: true)
                .AddEnvironmentVariables();
            Configuration = builder.Build();
        }

        public IConfigurationRoot Configuration { get; }

        // This method gets called by the runtime. Use this method to add services to the container.
        public void ConfigureServices(IServiceCollection services)
        {
            // Add framework services.
            services.AddMvc();
            services.AddMemoryCache();
            services.AddSingleton<IConfiguration>(Configuration);

            services.AddTransient(sp => new GithubGateway(
                Configuration.GetValue<string>(ConfigurationKeys.APP_TARGET_USER),
                Configuration.GetValue<string>(ConfigurationKeys.APP_TARGET_REPO),
                sp.GetService<ILoggerFactory>().CreateLogger(typeof(GithubGateway))));

            services.AddSingleton<GithubService>();
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IHostingEnvironment env, ILoggerFactory loggerFactory)
        {
            loggerFactory.AddConsole(Configuration.GetSection("Logging"));
            loggerFactory.AddDebug();

            app.UseMvc();
        }
    }
}
