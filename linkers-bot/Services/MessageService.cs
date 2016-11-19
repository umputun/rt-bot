using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace LinkAggregatorBot.Services
{

    public interface IMessageService
    {
        Task<IEnumerable<ExtMessage>> GetLinksAsync();
        Task<string> GetMDLinksAsync();
        Task<bool> ProcessMessage(Message message);
        Task<ISet<string>> GetCommands();
    }

    public class MessageService : IMessageService
    {
        public static Lazy<IMessageService> instance = new Lazy<IMessageService>(() => { return new MessageService(); });
        public static ISet<string> commands { get; } = new HashSet<string>() { "ссылки", "дай ссылки", "links", "get links" };

        private readonly List<ExtMessage> storage = new List<ExtMessage>();
        private readonly ReaderWriterLockSlim rw = new ReaderWriterLockSlim();

        private MessageService()
        {
        }

        public static IMessageService GetInstance()
        {
            return instance.Value;
        }

        public Task<bool> ProcessMessage(Message message)
        {
            return Task.Run(() =>
            {
                if (message.Username == "rt-bot")
                {
                    if (message.Text.ToLower().Contains("официальный кат!"))
                    {
                        rw.EnterWriteLock();
                        try
                        {
                            storage.Clear();
                        }
                        catch
                        {
                            rw.ExitWriteLock();
                        }
                    }
                    return false;
                }
                if (commands.Contains(message?.Text.ToLower()))
                {
                    return true;
                }
                else
                {
                    if (message != null && message.Text.IndexOf("http", StringComparison.Ordinal) > -1)
                    {
                        rw.EnterWriteLock();
                        try
                        {
                            storage.Add(new ExtMessage
                            {
                                Username = message.Username,
                                Text = message.Text,
                                Display_name = message.Display_name,
                                MDMessage = $"<dt>{message.Display_name}</dt><dd>{message.Text}</dd>"
                            });
                        }
                        finally
                        {
                            rw.ExitWriteLock();
                        }
                    }
                    return false;
                }
            });
        }

        public Task<IEnumerable<ExtMessage>> GetLinksAsync()
        {
            return Task.Run(() =>
            {
                rw.EnterReadLock();
                try
                {
                    return storage.AsEnumerable();
                }
                finally
                {
                    rw.ExitReadLock();
                }
            });
        }

        public Task<ISet<string>> GetCommands()
        {
            return Task.Run(() =>
            {
                return commands;
            });
        }

        public async Task<string> GetMDLinksAsync()
        {
            var sb = new StringBuilder();
            sb.AppendLine("<dl>");
            foreach (var line in (await GetLinksAsync()).Select(x => x.MDMessage))
            {
                sb.Append(line);
            }
            sb.AppendLine("</dl>");
            return sb.ToString();
        }
    }

    public class Message
    {
        public string Text { get; set; }
        public string Username { get; set; }
        public string Display_name { get; set; }
    }

    public class ExtMessage : Message
    {
        public string MDMessage { get; set; }
    }
}