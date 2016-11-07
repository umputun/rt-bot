using Microsoft.AspNetCore.Mvc;
using memberberries.Models;
using memberberries.Services;

namespace memberberries.Controllers
{
    [Route("[controller]")]
    public class EventController : Controller
    {
        private readonly IBot _bot;
        public EventController(IBot bot)
        {
            _bot = bot;
        }

        // POST api/values
        [HttpPost]
        public IActionResult Post([FromBody] Message message)
        {
            var answer = _bot.GetAnswere(message);
            
            if (answer == null) {
                HttpContext.Response.StatusCode = 417;
                return null;
                
            }
            
            HttpContext.Response.StatusCode = 201;

            return new JsonResult(answer);
        }
    }
}
