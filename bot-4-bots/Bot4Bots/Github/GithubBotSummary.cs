namespace Bot4Bots.Github
{
    public class GithubBotSummary
    {
        public string Name { get; set; }
        public string Link { get; set; }
        public GithubCommitter CreatedBy { get; set; }
        public GithubCommitter LastChangedBy { get; set; }

    }
}