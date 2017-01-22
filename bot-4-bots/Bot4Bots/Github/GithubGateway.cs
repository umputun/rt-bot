using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using Newtonsoft.Json;
using HtmlAgilityPack;
using HtmlAgilityPack.CssSelectors.NetCore;
using System.Net;
using Microsoft.Extensions.Logging;

namespace Bot4Bots.Github
{
    public class GithubGateway
    {
        private readonly string _targetUser;
        private readonly string _targetRepo;
        private readonly ILogger _logger;
        private readonly HttpClient _client;

        public GithubGateway(string targetUser, string targetRepo, ILogger logger)
        {
            _targetUser = targetUser;
            _targetRepo = targetRepo;
            _logger = logger;

            _client = new HttpClient();
            _client.DefaultRequestHeaders.Accept.Clear();
            _client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("*/*"));
            _client.DefaultRequestHeaders.UserAgent.Clear();
            _client.DefaultRequestHeaders.UserAgent.Add(new ProductInfoHeaderValue("curl", "7.35.0"));
        }

        public string GetLastCommit()
        {
            var rootUri = $"https://api.github.com/repos/{_targetUser}/{_targetRepo}/commits";
            var response = _client.GetStringAsync(rootUri).Result;
            var commits = JsonConvert.DeserializeObject<List<GithubCommitItem>>(response);
            return commits.First().sha;
        }

        public IReadOnlyCollection<GithubBotSummary> GetSummary()
        {
            var rootContentItems = GetGithubContentItems();

            //using async methods to speed up concurrent network operations
            var tasks = rootContentItems
                            .Select(GetGithubBotSummaryAsync)
                            .ToArray();
            Task.WaitAll(tasks);

            return tasks
                .Select(x => x.Result)
                .Where(x => x != null)
                .ToArray();
        }

        private List<GithubContentItem> GetGithubContentItems(string path = null)
        {
            var rootUri = $"https://api.github.com/repos/{_targetUser}/{_targetRepo}/contents/{path}";
            var response = _client.GetStringAsync(rootUri).Result;
            var rootContentItems = JsonConvert.DeserializeObject<List<GithubContentItem>>(response);
            return rootContentItems;
        }

        private async Task<GithubBotSummary> GetGithubBotSummaryAsync(GithubContentItem rootContentItem)
        {
            if (rootContentItem.type != "dir")
                return null;

            if (!await FileExistsAsync(rootContentItem.path + "/bot-spec.yml").ConfigureAwait(false))
                return null;

            var committers = await GetCommitterInfoAsync(rootContentItem.path).ConfigureAwait(false);

            return new GithubBotSummary
            {
                Name = rootContentItem.name,
                CreatedBy = committers.Item1,
                LastChangedBy = committers.Item2,
                Link = $"https://github.com/{_targetUser}/{_targetRepo}/blob/master/{rootContentItem.path}"
            };
        }

        private async Task<Tuple<GithubCommitter, GithubCommitter>> GetCommitterInfoAsync(string path)
        {
            var uri = $"https://github.com/{_targetUser}/{_targetRepo}/commits/master/{path}";
            var html = await _client.GetStringAsync(uri).ConfigureAwait(false);

            var doc = new HtmlDocument();
            doc.LoadHtml(html);
            
            var authors = doc.DocumentNode.QuerySelectorAll("div.commit-meta.commit-author-section");

            var latestCommitterNode = authors.FirstOrDefault();
            var lastChangedBy = ParseCommitterInfo(latestCommitterNode);

            //TODO: we could have more than 1 page with commits.
            //in this case consider use recursion to get to the real first commit
            var createdByNode = authors.LastOrDefault();
            var createdBy = ParseCommitterInfo(createdByNode);

            return Tuple.Create(createdBy, lastChangedBy);
        }

        private static GithubCommitter ParseCommitterInfo(HtmlNode node)
        {
            var user = node.QuerySelector(".commit-author.user-mention")?.InnerHtml ?? "unknown";
            var dateString = node.QuerySelector("relative-time").GetAttributeValue("datetime", null);

            DateTime date;
            if (!DateTime.TryParse(dateString, out date)) date = new DateTime(2000, 01, 01);

            return new GithubCommitter
            {
                User = user,
                CommitDate = date
            };
        }

        private async Task<bool> FileExistsAsync(string path)
        {
            var uri = $"https://github.com/{_targetUser}/{_targetRepo}/blob/master/{path}";
            var request = new HttpRequestMessage(HttpMethod.Head, uri);
            var response = await _client.SendAsync(request).ConfigureAwait(false);

            if (response.StatusCode == HttpStatusCode.NotFound)
            {
                return false;
            }

            response.EnsureSuccessStatusCode();
            return true;
        }

        private class GithubContentItem
        {
            public string name { get; set; }
            public string path { get; set; }
            public string type { get; set; }
        }

        public class GithubCommitItem
        {
            public string sha { get; set; }
        }
    }
}
