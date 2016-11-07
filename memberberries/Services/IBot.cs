using memberberries.Models;

namespace memberberries.Services
{
    public interface IBot
    {
        Answer GetAnswere(Message message);
    }
}
