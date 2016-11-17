using Microsoft.AspNetCore.Mvc;
using memberberries.Models;
using memberberries.Services;

namespace memberberries.Controllers
{
    [Route("[controller]")]
    public class InfoController : Controller
    {
        private readonly IBot _bot;
        public InfoController(IBot bot)
        {
            _bot = bot;
        }

        // Get
        [HttpGet]
        public IActionResult Get()
        {
            return Ok(_bot.GetAbout());
        }
    }
}
