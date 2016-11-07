using memberberries.Models;
using System.Text.RegularExpressions;

namespace memberberries.Services
{
    public class Bot : IBot
    {
        private Regex pattern_en;
        private Regex pattern_ru;

        private const string botname = "MemberBerries";

        public Bot()
        {
            pattern_en = new Regex(
                "(member).*\\?",
                RegexOptions.Compiled | RegexOptions.IgnoreCase | RegexOptions.Multiline
            );

            pattern_ru = new Regex(
                "(помни).*\\?",
                RegexOptions.Compiled | RegexOptions.IgnoreCase | RegexOptions.Multiline
            );
        }

        public Answer GetAnswere(Message message)
        {
            var match_en = pattern_en.Match(
                message.text
            );

            if (match_en.Success) {
                return new Answer{
                    text = "Oh I member...",
                    bot = botname
                };
            }

            var match_ru = pattern_ru.Match(
                message.text
            );

            if (match_ru.Success) {
                return new Answer{
                    text = "О! Я помню...",
                    bot = botname
                };
            }

            return null;
        }
    }
}