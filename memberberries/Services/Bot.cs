using memberberries.Models;
using System.Text.RegularExpressions;

namespace memberberries.Services
{
    public class Bot : IBot
    {
        private Regex pattern_en;
        private Regex pattern_ru;

        private const string _botname = "MemberBerries";

        private const string _author = "Andrey Popov";

        private const string _info = "Шутливый бот Вспоминашки (MemberBerries) по мотивам сериала Южный Парк. Реагирует на фразы вида: `Помните то-то?`";

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

        public About GetAbout()
        {
            return new About {
                author = _author,

                info = _info,

                commands = null
            };
        }

        public Answer GetAnswere(Message message)
        {
            var match_en = pattern_en.Match(
                message.text
            );

            if (match_en.Success) {
                return new Answer{
                    text = "Oh I member...",
                    bot = _botname
                };
            }

            var match_ru = pattern_ru.Match(
                message.text
            );

            if (match_ru.Success) {
                return new Answer{
                    text = "О! Я помню...",
                    bot = _botname
                };
            }

            return null;
        }
    }
}