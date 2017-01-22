using System.Collections.Generic;
using System.Diagnostics;
using Microsoft.Extensions.Logging;

namespace Bot4Bots.Github
{
    public class GithubService
    {
        private IReadOnlyCollection<GithubBotSummary> _summaries = new GithubBotSummary[0];
        private string _lastCommitSha = null; 


        private readonly GithubGateway _gateway;
        private readonly ILogger _logger;

        public GithubService(GithubGateway gateway, ILogger<GithubGateway> logger)
        {
            _gateway = gateway;
            _logger = logger;
        }

        public IReadOnlyCollection<GithubBotSummary> GetSummaries()
        {
            return _summaries;
        }

        public void LoadSummaries()
        {
            _logger.LogInformation("Loading bots from Github..");

            var lastCommitSha = _gateway.GetLastCommit();
            _logger.LogInformation($"Loaded last commit SHA: '{lastCommitSha}', in cache: '{_lastCommitSha}'");
            
            if (lastCommitSha != _lastCommitSha)
            {
                _lastCommitSha = lastCommitSha;

                var ts = Stopwatch.StartNew();
                _summaries = _gateway.GetSummary();
                ts.Stop();

                _logger.LogInformation("{0} bots were loaded from Github in {1}", _summaries.Count, ts.Elapsed);
            }
            else 
            {
                _logger.LogInformation("Nothing was changed since last check. Loading was skipped.");
            }
        }
    }
}
