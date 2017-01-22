using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using Bot4Bots.Github;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;

namespace Bot4Bots
{
    [Route("")]
    public class BotController : Controller
    {
        private static readonly string NewLine = @"\n";
        private static readonly string BotName = "bot-4-bots"; 

        private static readonly Dictionary<string,string> BotsSummaryCommands = new Dictionary<string, string>
        {
            { "/bots summary", "returns bot's summary from Github: created date, last changed date etc.." },
            { "/сводка ботов", "возвращает сводку о ботах из Github: когда и кем бот был создан и последний раз изменен" }
        };

        private readonly GithubService _githubService;
        private readonly ILogger _logger;
        
        public BotController(GithubService githubService, ILogger<BotController> logger)
        {
            _githubService = githubService;
            _logger = logger;
        }

        [HttpGet("info")]
        public InfoModel Info(int id)
        {
            return new InfoModel
            {
                Author = "khaale",
                Info = $"{BotName} - показывает расширенную информацию о ботах",
                Commands = BotsSummaryCommands.Select(x => $"{x.Key} - {x.Value}").ToArray()
            };
        }
        
        [HttpPost("event")]
        public IActionResult Event([FromBody] EventModel evt)
        {
            _logger.LogDebug($"Received event, text: '{evt.Text}'");
            if (IsBotsStatsRequest(evt))
            {
                _logger.LogDebug("Getting new bots");
                var message = GetBotsSummary();
                var messageModel = new EventResponseModel
                {
                    Text = message,
                    Bot = BotName
                };

                return Created("",messageModel);
            }
            else
            {
                return StatusCode((int)HttpStatusCode.ExpectationFailed);
            }
        }

        private bool IsBotsStatsRequest(EventModel evt)
        {
            return BotsSummaryCommands.Keys.Contains(evt.Text?.Trim());
        }

        private string GetBotsSummary()
        {
            var githubBotSummaries = _githubService.GetSummaries();

            if (!githubBotSummaries.Any())
            {
                return "Sorry, Github data have not been loaded yet :(";
            }

            var tableRows = (
                from bi in githubBotSummaries
                orderby bi.CreatedBy?.CommitDate descending
                select $"[{bi.Name}]({bi.Link})|" +
                    $"{bi.CreatedBy?.CommitDate:d}|{bi.CreatedBy?.User}|" +
                    $"{bi.LastChangedBy?.CommitDate:d}|{bi.LastChangedBy?.User}"
                ).ToList();

            var tableHeader = new[]
            {
                    NewLine + NewLine + "Bot Name | Created On &darr; | Created By | Last Changed On | Last Changed By",
                                        "---------|-------------------|------------|-----------------|----------------"
            };

            var message = string.Join(NewLine, tableHeader.Concat(tableRows));

            return message;
        }

        public class InfoModel
        {
            [JsonProperty("author")] public string Author { get; set; }
            [JsonProperty("info")] public string Info { get; set; }
            [JsonProperty("commands")] public string[] Commands { get; set; }
        }

        public class EventModel
        {
            [JsonProperty("text")] public string Text { get; set; }
            [JsonProperty("username")] public string UserName { get; set; }
            [JsonProperty("display_name")] public string DisplayName { get; set; }
        }

        public class EventResponseModel
        {
            [JsonProperty("text")] public string Text { get; set; }
            [JsonProperty("bot")] public string Bot { get; set; }
        }
    }
}
