open FSharp.Data
open Suave
open Suave.Filters
open Suave.Web
open Suave.Successful
open Suave.Operators

let appId = System.Environment.GetEnvironmentVariable "RADIOT_WOT_BOT_APPID"

//
// URLs to API
//
let urlAccountList = "https://api.worldoftanks.ru/wot/account/list/"
let urlAccountAchievements = "https://api.worldoftanks.ru/wot/account/achievements/"
let urlAccountTanks = "https://api.worldoftanks.ru/wot/account/tanks/"
let urlAccountInfo = "https://api.worldoftanks.ru/wot/account/info/"
let urlTankInfo = "https://api.worldoftanks.ru/wot/encyclopedia/vehicles/"


// message from chat to bot
type RawIncomingMessage = JsonProvider<"""{"text": "wot стата az_ainamart", "username": "id пользователя", "display_name": "имя пользователя" }""">

// response from urlAccountList
type PlayerResponse = JsonProvider<"""{"status":"ok","meta":{"count":1},"data":[{"nickname":"Az_Ainamart","account_id":1233890}]}""">

// response from urlAccountTanks
type PlayerTanksResponse = JsonProvider<"""{"status":"ok","meta":{"count":1},"data":{"1233890":[{"statistics":{"wins":792,"battles":1498},"mark_of_mastery":4,"tank_id":54289},{"statistics":{"wins":596,"battles":1177},"mark_of_mastery":4,"tank_id":6657},{"statistics":{"wins":464,"battles":930},"mark_of_mastery":4,"tank_id":4353},{"statistics":{"wins":416,"battles":832},"mark_of_mastery":4,"tank_id":7425},{"statistics":{"wins":318,"battles":618},"mark_of_mastery":3,"tank_id":13825},{"statistics":{"wins":316,"battles":577},"mark_of_mastery":4,"tank_id":51457},{"statistics":{"wins":239,"battles":474},"mark_of_mastery":4,"tank_id":9217},{"statistics":{"wins":252,"battles":433},"mark_of_mastery":4,"tank_id":55569},{"statistics":{"wins":214,"battles":423},"mark_of_mastery":3,"tank_id":5633},{"statistics":{"wins":170,"battles":364},"mark_of_mastery":4,"tank_id":7169},{"statistics":{"wins":167,"battles":347},"mark_of_mastery":0,"tank_id":2561},{"statistics":{"wins":157,"battles":346},"mark_of_mastery":4,"tank_id":2305},{"statistics":{"wins":166,"battles":321},"mark_of_mastery":3,"tank_id":18209},{"statistics":{"wins":153,"battles":315},"mark_of_mastery":4,"tank_id":63553},{"statistics":{"wins":159,"battles":295},"mark_of_mastery":4,"tank_id":257},{"statistics":{"wins":158,"battles":288},"mark_of_mastery":3,"tank_id":7681}]}}""">
type PlayerTanksData = JsonProvider<"""{"statistics":{"wins":792,"battles":1498},"mark_of_mastery":4,"tank_id":54289}""">

// response from urlTankInfo
type TankNameResponse = JsonProvider<"""{"status":"ok","meta":{"count":1},"data":{"13825":{"name":"Т-62А"}}}""">

// response from urlAccountInfo
type PlayerInfoResponse = JsonProvider<"""{"status":"ok","meta":{"count":1},"data":{"1233890":{"client_language":"ru","last_battle_time":1479494551,"account_id":1233890,"created_at":1297367221,"updated_at":1479504795,"private":null,"ban_time":null,"global_rating":6077,"clan_id":193502,"statistics":{"clan":{"spotted":0,"avg_damage_assisted_track":0.0,"avg_damage_blocked":0.0,"direct_hits_received":0,"explosion_hits":0,"piercings_received":0,"piercings":0,"xp":0,"survived_battles":0,"dropped_capture_points":0,"hits_percents":0,"draws":0,"battles":0,"damage_received":0,"avg_damage_assisted":0.0,"frags":0,"avg_damage_assisted_radio":0.0,"capture_points":0,"hits":0,"battle_avg_xp":0,"wins":0,"losses":0,"damage_dealt":0,"no_damage_direct_hits_received":0,"shots":0,"explosion_hits_received":0,"tanking_factor":0.0},"all":{"spotted":19821,"avg_damage_assisted_track":85.76,"max_xp":2499,"avg_damage_blocked":441.75,"direct_hits_received":41626,"explosion_hits":1437,"piercings_received":28507,"piercings":35524,"max_damage_tank_id":8193,"xp":8178841,"survived_battles":3504,"dropped_capture_points":13018,"hits_percents":64,"draws":197,"max_xp_tank_id":63553,"battles":15290,"damage_received":13523210,"avg_damage_assisted":482.46,"max_frags_tank_id":54273,"frags":12588,"avg_damage_assisted_radio":396.7,"capture_points":15019,"max_damage":8401,"hits":91910,"battle_avg_xp":535,"wins":7849,"losses":7244,"damage_dealt":14561450,"no_damage_direct_hits_received":13119,"max_frags":10,"shots":144736,"explosion_hits_received":1559,"tanking_factor":0.39},"regular_team":{"spotted":0,"avg_damage_assisted_track":0.0,"max_xp":0,"avg_damage_blocked":0.0,"direct_hits_received":0,"explosion_hits":0,"piercings_received":0,"piercings":0,"max_damage_tank_id":null,"xp":0,"survived_battles":0,"dropped_capture_points":0,"hits_percents":0,"draws":0,"max_xp_tank_id":null,"battles":0,"damage_received":0,"avg_damage_assisted":0.0,"max_frags_tank_id":null,"frags":0,"avg_damage_assisted_radio":0.0,"capture_points":0,"max_damage":0,"hits":0,"battle_avg_xp":0,"wins":0,"losses":0,"damage_dealt":0,"no_damage_direct_hits_received":0,"max_frags":0,"shots":0,"explosion_hits_received":0,"tanking_factor":0.0},"trees_cut":12399,"company":{"spotted":2,"avg_damage_assisted_track":0.0,"avg_damage_blocked":0.0,"direct_hits_received":0,"explosion_hits":0,"piercings_received":0,"piercings":0,"xp":74,"survived_battles":0,"dropped_capture_points":0,"hits_percents":0,"draws":0,"battles":2,"damage_received":960,"avg_damage_assisted":0.0,"frags":0,"avg_damage_assisted_radio":0.0,"capture_points":0,"hits":0,"battle_avg_xp":37,"wins":0,"losses":2,"damage_dealt":0,"no_damage_direct_hits_received":0,"shots":0,"explosion_hits_received":0,"tanking_factor":0.0},"stronghold_skirmish":{"spotted":0,"max_frags_tank_id":null,"max_xp":0,"direct_hits_received":0,"explosion_hits":0,"piercings_received":0,"piercings":0,"xp":0,"survived_battles":0,"dropped_capture_points":0,"hits_percents":0,"draws":0,"max_xp_tank_id":null,"battles":0,"damage_received":0,"frags":0,"capture_points":0,"max_damage_tank_id":null,"max_damage":0,"hits":0,"battle_avg_xp":0,"wins":0,"losses":0,"damage_dealt":0,"no_damage_direct_hits_received":0,"max_frags":0,"shots":0,"explosion_hits_received":0,"tanking_factor":0.0},"stronghold_defense":{"spotted":0,"max_frags_tank_id":null,"max_xp":0,"direct_hits_received":0,"explosion_hits":0,"piercings_received":0,"piercings":0,"xp":0,"survived_battles":0,"dropped_capture_points":0,"hits_percents":0,"draws":0,"max_xp_tank_id":null,"battles":0,"damage_received":0,"frags":0,"capture_points":0,"max_damage_tank_id":null,"max_damage":0,"hits":0,"battle_avg_xp":0,"wins":0,"losses":0,"damage_dealt":0,"no_damage_direct_hits_received":0,"max_frags":0,"shots":0,"explosion_hits_received":0,"tanking_factor":0.0},"historical":{"spotted":0,"avg_damage_assisted_track":0.0,"max_xp":0,"avg_damage_blocked":0.0,"direct_hits_received":0,"explosion_hits":0,"piercings_received":0,"piercings":0,"max_damage_tank_id":null,"xp":0,"survived_battles":0,"dropped_capture_points":0,"hits_percents":0,"draws":0,"max_xp_tank_id":null,"battles":0,"damage_received":0,"avg_damage_assisted":0.0,"max_frags_tank_id":null,"frags":0,"avg_damage_assisted_radio":0.0,"capture_points":0,"max_damage":0,"hits":0,"battle_avg_xp":0,"wins":0,"losses":0,"damage_dealt":0,"no_damage_direct_hits_received":0,"max_frags":0,"shots":0,"explosion_hits_received":0,"tanking_factor":0.0},"team":{"spotted":14,"avg_damage_assisted_track":0.0,"max_xp":0,"avg_damage_blocked":0.0,"direct_hits_received":50,"explosion_hits":0,"piercings_received":42,"piercings":32,"max_damage_tank_id":null,"xp":5607,"survived_battles":3,"dropped_capture_points":0,"hits_percents":78,"draws":0,"max_xp_tank_id":null,"battles":11,"damage_received":13404,"avg_damage_assisted":39.18,"max_frags_tank_id":null,"frags":4,"avg_damage_assisted_radio":39.18,"capture_points":25,"max_damage":0,"hits":45,"battle_avg_xp":510,"wins":4,"losses":7,"damage_dealt":10749,"no_damage_direct_hits_received":8,"max_frags":0,"shots":58,"explosion_hits_received":0,"tanking_factor":0.0},"frags":null},"nickname":"Az_Ainamart","ban_info":null,"logout_at":1479504792}}}""">
type PlayerInfoData = JsonProvider<"""{"client_language":"ru","last_battle_time":1479494551,"account_id":1233890,"created_at":1297367221,"updated_at":1479504795,"private":null,"ban_time":null,"global_rating":6077,"clan_id":193502,"statistics":{"clan":{"spotted":0,"avg_damage_assisted_track":0.0,"avg_damage_blocked":0.0,"direct_hits_received":0,"explosion_hits":0,"piercings_received":0,"piercings":0,"xp":0,"survived_battles":0,"dropped_capture_points":0,"hits_percents":0,"draws":0,"battles":0,"damage_received":0,"avg_damage_assisted":0.0,"frags":0,"avg_damage_assisted_radio":0.0,"capture_points":0,"hits":0,"battle_avg_xp":0,"wins":0,"losses":0,"damage_dealt":0,"no_damage_direct_hits_received":0,"shots":0,"explosion_hits_received":0,"tanking_factor":0.0},"all":{"spotted":19821,"avg_damage_assisted_track":85.76,"max_xp":2499,"avg_damage_blocked":441.75,"direct_hits_received":41626,"explosion_hits":1437,"piercings_received":28507,"piercings":35524,"max_damage_tank_id":8193,"xp":8178841,"survived_battles":3504,"dropped_capture_points":13018,"hits_percents":64,"draws":197,"max_xp_tank_id":63553,"battles":15290,"damage_received":13523210,"avg_damage_assisted":482.46,"max_frags_tank_id":54273,"frags":12588,"avg_damage_assisted_radio":396.7,"capture_points":15019,"max_damage":8401,"hits":91910,"battle_avg_xp":535,"wins":7849,"losses":7244,"damage_dealt":14561450,"no_damage_direct_hits_received":13119,"max_frags":10,"shots":144736,"explosion_hits_received":1559,"tanking_factor":0.39},"regular_team":{"spotted":0,"avg_damage_assisted_track":0.0,"max_xp":0,"avg_damage_blocked":0.0,"direct_hits_received":0,"explosion_hits":0,"piercings_received":0,"piercings":0,"max_damage_tank_id":null,"xp":0,"survived_battles":0,"dropped_capture_points":0,"hits_percents":0,"draws":0,"max_xp_tank_id":null,"battles":0,"damage_received":0,"avg_damage_assisted":0.0,"max_frags_tank_id":null,"frags":0,"avg_damage_assisted_radio":0.0,"capture_points":0,"max_damage":0,"hits":0,"battle_avg_xp":0,"wins":0,"losses":0,"damage_dealt":0,"no_damage_direct_hits_received":0,"max_frags":0,"shots":0,"explosion_hits_received":0,"tanking_factor":0.0},"trees_cut":12399,"company":{"spotted":2,"avg_damage_assisted_track":0.0,"avg_damage_blocked":0.0,"direct_hits_received":0,"explosion_hits":0,"piercings_received":0,"piercings":0,"xp":74,"survived_battles":0,"dropped_capture_points":0,"hits_percents":0,"draws":0,"battles":2,"damage_received":960,"avg_damage_assisted":0.0,"frags":0,"avg_damage_assisted_radio":0.0,"capture_points":0,"hits":0,"battle_avg_xp":37,"wins":0,"losses":2,"damage_dealt":0,"no_damage_direct_hits_received":0,"shots":0,"explosion_hits_received":0,"tanking_factor":0.0},"stronghold_skirmish":{"spotted":0,"max_frags_tank_id":null,"max_xp":0,"direct_hits_received":0,"explosion_hits":0,"piercings_received":0,"piercings":0,"xp":0,"survived_battles":0,"dropped_capture_points":0,"hits_percents":0,"draws":0,"max_xp_tank_id":null,"battles":0,"damage_received":0,"frags":0,"capture_points":0,"max_damage_tank_id":null,"max_damage":0,"hits":0,"battle_avg_xp":0,"wins":0,"losses":0,"damage_dealt":0,"no_damage_direct_hits_received":0,"max_frags":0,"shots":0,"explosion_hits_received":0,"tanking_factor":0.0},"stronghold_defense":{"spotted":0,"max_frags_tank_id":null,"max_xp":0,"direct_hits_received":0,"explosion_hits":0,"piercings_received":0,"piercings":0,"xp":0,"survived_battles":0,"dropped_capture_points":0,"hits_percents":0,"draws":0,"max_xp_tank_id":null,"battles":0,"damage_received":0,"frags":0,"capture_points":0,"max_damage_tank_id":null,"max_damage":0,"hits":0,"battle_avg_xp":0,"wins":0,"losses":0,"damage_dealt":0,"no_damage_direct_hits_received":0,"max_frags":0,"shots":0,"explosion_hits_received":0,"tanking_factor":0.0},"historical":{"spotted":0,"avg_damage_assisted_track":0.0,"max_xp":0,"avg_damage_blocked":0.0,"direct_hits_received":0,"explosion_hits":0,"piercings_received":0,"piercings":0,"max_damage_tank_id":null,"xp":0,"survived_battles":0,"dropped_capture_points":0,"hits_percents":0,"draws":0,"max_xp_tank_id":null,"battles":0,"damage_received":0,"avg_damage_assisted":0.0,"max_frags_tank_id":null,"frags":0,"avg_damage_assisted_radio":0.0,"capture_points":0,"max_damage":0,"hits":0,"battle_avg_xp":0,"wins":0,"losses":0,"damage_dealt":0,"no_damage_direct_hits_received":0,"max_frags":0,"shots":0,"explosion_hits_received":0,"tanking_factor":0.0},"team":{"spotted":14,"avg_damage_assisted_track":0.0,"max_xp":0,"avg_damage_blocked":0.0,"direct_hits_received":50,"explosion_hits":0,"piercings_received":42,"piercings":32,"max_damage_tank_id":null,"xp":5607,"survived_battles":3,"dropped_capture_points":0,"hits_percents":78,"draws":0,"max_xp_tank_id":null,"battles":11,"damage_received":13404,"avg_damage_assisted":39.18,"max_frags_tank_id":null,"frags":4,"avg_damage_assisted_radio":39.18,"capture_points":25,"max_damage":0,"hits":45,"battle_avg_xp":510,"wins":4,"losses":7,"damage_dealt":10749,"no_damage_direct_hits_received":8,"max_frags":0,"shots":58,"explosion_hits_received":0,"tanking_factor":0.0},"frags":null},"nickname":"Az_Ainamart","ban_info":null,"logout_at":1479504792}""">

// response from urlAccountAchievements
type AchievementsResponse = JsonProvider<"""{"status":"ok","meta":{"count":1},"data":{"1233890":{"achievements":{"medalCarius":1,"aimer":5,"invader":13,"medalFadin":1,"armorPiercer":77,"medalEkins":1,"tankExpert3":1,"medalKay":2,"duelist":169,"markIRepairer":1,"defender":39,"medalLeClerc":2,"demolition":50,"supporter":138,"steelwall":120,"tankExpert0":1,"medalAbrams":2,"tankExpert1":1,"medalPoppel":2,"medalPascucci":16,"operationWinter":1,"reliableComrade":31,"markIBaseProtector":1,"luckyDevil":9,"markIBomberman":2,"mainGun":124,"kamikaze":10,"sinai":12,"sniper":190,"bonecrusher":590,"titleSniper":259,"deathTrack":2,"warrior":67,"even":13,"medalKolobanov":2,"scout":38,"beasthunter":7,"medalGore":3,"fallout":1,"ironMan":86,"markI100Years":3,"tankExpert2":1,"medalRadleyWalters":3,"bombardier":5,"tankExpert6":1,"sniper2":23,"arsonist":50,"charmed":53,"medalBillotte":2,"fighter":108,"medalLavrinenko":2,"impenetrable":99,"sturdy":56,"markIProtector":1,"medalKnispel":1,"falloutSteelHunter":1,"handOfDeath":6,"battleCitizen":1,"WFC2014":2,"shootToKill":1310,"medalDumitru":1,"evileye":19,"firstMerit":1,"tankExpert5":1},"frags":{"beasthunter":774,"sinai":1233,"pattonValley":23},"max_series":{"armorPiercer":77,"aimer":5,"titleSniper":259,"tacticalBreakthrough":0,"invincible":3,"victoryMarch":0,"deathTrack":2,"EFC2016":0,"diehard":6,"WFC2014":2,"handOfDeath":6}}}}""">
type AchievementsData = JsonProvider<"""{"achievements":{"medalCarius":1,"aimer":5,"invader":13,"medalFadin":1,"armorPiercer":77,"medalEkins":1,"tankExpert3":1,"medalKay":2,"duelist":169,"markIRepairer":1,"defender":39,"medalLeClerc":2,"demolition":50,"supporter":138,"steelwall":120,"tankExpert0":1,"medalAbrams":2,"tankExpert1":1,"medalPoppel":2,"medalPascucci":16,"operationWinter":1,"reliableComrade":31,"markIBaseProtector":1,"luckyDevil":9,"markIBomberman":2,"mainGun":124,"kamikaze":10,"sinai":12,"sniper":190,"bonecrusher":590,"titleSniper":259,"deathTrack":2,"warrior":67,"even":13,"medalKolobanov":2,"scout":38,"beasthunter":7,"medalGore":3,"fallout":1,"ironMan":86,"markI100Years":3,"tankExpert2":1,"medalRadleyWalters":3,"bombardier":5,"tankExpert6":1,"sniper2":23,"arsonist":50,"charmed":53,"medalBillotte":2,"fighter":108,"medalLavrinenko":2,"impenetrable":99,"sturdy":56,"markIProtector":1,"medalKnispel":1,"falloutSteelHunter":1,"handOfDeath":6,"battleCitizen":1,"WFC2014":2,"shootToKill":1310,"medalDumitru":1,"evileye":19,"firstMerit":1,"tankExpert5":1},"frags":{"beasthunter":774,"sinai":1233,"pattonValley":23},"max_series":{"armorPiercer":77,"aimer":5,"titleSniper":259,"tacticalBreakthrough":0,"invincible":3,"victoryMarch":0,"deathTrack":2,"EFC2016":0,"diehard":6,"WFC2014":2,"handOfDeath":6}}""">


let medals =
  [| "Медаль героев Расейняя",  "heroesOfRassenay";
     "Медаль Пула", "medalLafayettePool";
     "Медаль Рэдли-Уолтерса", "medalRadleyWalters";
     "Медаль Колобанова", "medalKolobanov";
     "Медаль Гора", "medalGore";
     "Медаль Бурды", "medalBurda";
     "Медаль Думитру", "medalDumitru";
     "Медаль де Ланглада", "medalDeLanglade";
     "Медаль Фадина", "medalFadin";
  |]

// if something is not ok, than return 417 code
let answerToChat s =
  match s with
  | Some t -> OK t
  | None -> "" |> OK >=> Writers.setStatus HttpCode.HTTP_417


// returns (accountID * name) so we can later ask info about player by its accountID
let getAccountId search =
  try
    let t = Http.RequestString("http://www.google.com", httpMethod = "GET")
    let playerResponseRaw = Http.RequestString (urlAccountList, httpMethod = "GET", query = ["application_id", appId; "search", search], timeout=3000)
    let playerResponse = playerResponseRaw |> PlayerResponse.Parse
    match playerResponse.Data.Length with
    | 0 -> 
      None
    | _ -> 
      let player = playerResponse.Data |> Array.head  // we need only first item, because it matches completly with search string
      match player.Nickname = search with
      | true -> 
        Some (player.AccountId, search)
      | false -> 
        None
  with
    | :? System.Exception as e ->  // don't care - can't do anything anyway
      None


// we have a list of player's tanks ids, but we need tanks names
let getTanksNames (tankIds:int[]) = 
  try
    let ids = tankIds |> Array.map(fun i -> i.ToString()) |> String.concat ","
    let response = Http.RequestString (urlTankInfo, httpMethod = "GET", query = ["application_id", appId; "tank_id", ids; "fields", "name"], timeout=3000)
                   |> TankNameResponse.Parse
    let tankNames = tankIds
                    |> Array.map(fun i -> (i, (i.ToString() |> response.Data.JsonValue.Item).Item("name").AsString())) |> dict
    Some tankNames
  with
  | :? System.Exception as e ->  // don't care - can't do anything anyway
    None
  

let getPlayerTanks (accIdName:(int*string) Option) =
  match accIdName with
  | Some (accId, name) ->
    try
      let response = Http.RequestString (urlAccountTanks, httpMethod = "GET", query = ["application_id", appId; "account_id", accId.ToString()], timeout=3000)
                     |> PlayerTanksResponse.Parse
      let tanksData = accId.ToString() |> response.Data.JsonValue.Item
      let tanks = tanksData.AsArray()
                  |> Array.map(fun i -> i.ToString() |> PlayerTanksData.Parse)
                  |> Array.sortByDescending(fun i -> i.Statistics.Battles)
                  |> Array.splitAt 5 |> fst
      let tankIds = tanks |> Array.map (fun t -> t.TankId)
      let tanksNamesOpt = getTanksNames tankIds
      match tanksNamesOpt with
      | Some tanksNames ->
        let tanksString = tanks
                          |> Array.map(fun t -> (tanksNames.Item t.TankId, t.Statistics.Battles, t.Statistics.Wins))
                          |> Array.map(fun (name, battles, wins) -> sprintf "\n%s: битв - %d, побед - %d (%d%%)" name battles wins ((100*wins)/battles))
                          |> Array.fold (fun acc s -> String.concat "" [acc; s]) (sprintf "Основные танки игрока %s" name)
        Some tanksString
      | _ -> None
    with
    | :? System.Exception as e ->  // don't care - can't do anything anyway
      None
  | None ->
    None


let getPlayerAchievements (accIdName:(int*string) Option) = 
  match accIdName with
  | Some (accId, name) -> 
    try
      let achievementsResponse = Http.RequestString (urlAccountAchievements, httpMethod = "GET", query = ["application_id", appId; "account_id", accId.ToString()], timeout=3000)
                                 |> AchievementsResponse.Parse
      let data = (achievementsResponse.Data.JsonValue.Item (accId.ToString())).ToString() |> AchievementsData.Parse

      let playerMedalsIds = data.Achievements.JsonValue.Properties()
                         |> Array.map fst
    
      let resultMedals = medals
                         |> Array.filter (fun (k, v) ->  playerMedalsIds |> Array.contains v)
    
      match resultMedals.Length with
      | x when x > 0 -> let resultString = resultMedals
                                           |> Array.map (fun (k, v) -> String.concat " " [k; (data.Achievements.JsonValue.Item(v)).ToString()])
                                           |> Array.fold (fun acc s -> String.concat "\n" [acc; s]) (sprintf "Медальки игрока %s" name)
                  
                        Some resultString
      | _ -> Some (sprintf "У %s особых медалек" name)
    with
    | :? System.Exception as e -> None  // don't care - can't do anything anyway
  | None ->
    None


let getPlayerStats (accIdName:(int*string) Option) = 
  match accIdName with
  | Some (accId, name) -> 
    try
      let achievementsResponse = Http.RequestString (urlAccountInfo, httpMethod = "GET", query = ["application_id", appId; "account_id", accId.ToString()], timeout=3000)
                                 |> PlayerInfoResponse.Parse
      let response = achievementsResponse.Data.JsonValue.Item (accId.ToString())
      let stats = response.ToString() |> PlayerInfoData.Parse
      let s = stats.Statistics.All
      Some (sprintf "Стата (общая) игрока %s:\nЗадрочено %d боёв, %d%% побед.\nДамажка за бой в среднем %d" name s.Battles (100*s.Wins/s.Battles) (s.DamageDealt/s.Battles))
    with
    | :? System.Exception as e -> None  // don't care - can't do anything anyway
  | None ->
    None
  

let parseMessage (s:string) =
  let a = s.Split ' '
  match a.[0], a.[1] with
  | "wotbot", "stat" -> getAccountId a.[2] |> getPlayerStats |> answerToChat
  | "wotbot", "medals" -> getAccountId a.[2] |> getPlayerAchievements |> answerToChat
  | "wotbot", "tanks" -> getAccountId a.[2] |> getPlayerTanks |> answerToChat
  | _ -> "" |> OK >=> Writers.setStatus HttpCode.HTTP_417
  
let processRequest (r:HttpRequest) =
  let s = System.Text.Encoding.UTF8.GetString r.rawForm
  let message = RawIncomingMessage.Parse s
  parseMessage message.Text

let config = {defaultConfig with bindings = [HttpBinding.mk HTTP (System.Net.IPAddress.Parse "0.0.0.0") 8080us]}
let app =
  choose
    [ GET >=>  path "/info" >=> OK "About bot"
      POST >=> path "/event" >=> request (fun r -> processRequest r ) ]

startWebServer config app