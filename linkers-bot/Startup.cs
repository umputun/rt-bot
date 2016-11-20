using System.IO;
using LinkAggregatorBot.Services;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;

namespace LinkAggregatorBot
{
    public class Startup
    {
        private static string commandsArrStr;
        private static IMessageService service = MessageService.GetInstance();
        public Startup(IHostingEnvironment env)
        {
            var builder = new ConfigurationBuilder()
                .SetBasePath(env.ContentRootPath)
                .AddJsonFile("appsettings.json", optional: true, reloadOnChange: true)
                .AddJsonFile($"appsettings.{env.EnvironmentName}.json", optional: true);

            Configuration = builder.Build();
        }

        public IConfigurationRoot Configuration { get; }

        // This method gets called by the runtime. Use this method to add services to the container.
        public void ConfigureServices(IServiceCollection services)
        {
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IHostingEnvironment env, ILoggerFactory loggerFactory)
        {
            commandsArrStr = string.Join("', '", service.GetCommands().Result);

            app.MapWhen((context) =>
            {
                return context.Request.Path.Value.ToString().EndsWith("/info") && context.Request.Method == "GET";
            },
            (inApp) =>
            {
                inApp.Run(async (context) =>
                {
                    using (var writer = new StreamWriter(context.Response.Body))
                    {
                        await writer.WriteAsync(@"{author = 'MrPink',info: 'Возвращает ссылки, опубликованные в чатике во время и немного после выпуска',commands:['" + commandsArrStr + "']}");
                    }
                });
            });

            app.MapWhen((context) =>
            {
                return context.Request.Path.Value.ToString().EndsWith("/event") && context.Request.Method == "POST";
            },
            (inApp) =>
            {
                inApp.Run(async (context) =>
                {
                    using (var reader = new StreamReader(context.Request.Body))
                    using (var writer = new StreamWriter(context.Response.Body))
                    {
                        var msg = JsonConvert.DeserializeObject<Message>(await reader.ReadToEndAsync());
                        var result = await service.ProcessMessage(msg);
                        context.Response.StatusCode = result ? 200 : 417;
                        if (result)
                        {
                            await writer.WriteAsync(JsonConvert.SerializeObject(
                                new
                                {
                                    text = await service.GetMDLinksAsync(),
                                    bot = "rt-bot-linkers"
                                }));
                        }
                    }
                });
            });
        }
    }
}
