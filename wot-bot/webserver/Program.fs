open FSharp.Data
open Suave
open Suave.Filters
open Suave.Web
open Suave.Successful
open Suave.Operators
open WOTBOT.Types

let definePercentage x =
  match x with
  | x when x < 40.0f -> sprintf "Рачина днищенская - %f%%" x
  | x when x < 45.0f -> sprintf "Олень образцовый - рейт %f%%" x
  | x when x < 48.0f -> sprintf "Рак обыкновенный - рейт %f%%" x
  | x when x < 49.0f -> sprintf "Ну такой... - рейт %f%%" x
  | x when x < 51.0f -> sprintf "Ничего особенного - рейт %f%%" x
  | x when x < 52.0f -> sprintf "Даже тащит - рейт %f%%" x
  | x when x < 55.0f -> sprintf "Кажется задрот - рейт %f%%" x
  | x when x < 58.0f -> sprintf "Прямые руки! - рейт %f%%" x
  | _ -> sprintf "Киберкотлета! Ну или вододел - рейт %f%%" x

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


let appId = System.Environment.GetEnvironmentVariable "RADIOT_WOT_BOT_APPID"
match appId with
| "" -> printf "APP_ID not found in ENV"
| _ -> printf "APP_ID has been found. Working."
let urlAccountList = "https://api.worldoftanks.ru/wot/account/list/"
let urlAccountAchievements = "https://api.worldoftanks.ru/wot/account/achievements/"
let urlAccountTanks = "https://api.worldoftanks.ru/wot/account/tanks/"
let urlAccountInfo = "https://api.worldoftanks.ru/wot/account/info/"
let urlTankInfo = "https://api.worldoftanks.ru/wot/encyclopedia/vehicles/"


let getAccountId search =
  try
    let t = Http.RequestString("http://www.google.com", httpMethod = "GET")
    let playerResponseRaw = Http.RequestString (urlAccountList, httpMethod = "GET", query = ["application_id", appId; "search", search], timeout=3000)
    let playerResponse = playerResponseRaw |> PlayerResponse.Parse
    match playerResponse.Data.Length with
    | 0 -> 
      None
    | _ -> 
      let player = playerResponse.Data |> Array.head
      match player.Nickname = search with
      | true -> 
        Some (player.AccountId, search)
      | false -> 
        None
  with
    | :? System.Exception as e -> 
      printfn "getAccountId exception %A" e
      None

let answerToChat s =
  match s with
  | Some t -> OK t
  | None -> "" |> OK >=> Writers.setStatus HttpCode.HTTP_417

let getTanksNames (tankIds:int[]) = 
  try
    let ids = tankIds |> Array.map(fun i -> i.ToString()) |> String.concat ","
    let response = Http.RequestString (urlTankInfo, httpMethod = "GET", query = ["application_id", appId; "tank_id", ids; "fields", "name"], timeout=3000)
                   |> TankNameResponse.Parse
    let tankNames = tankIds
                    |> Array.map(fun i -> (i, (i.ToString() |> response.Data.JsonValue.Item).Item("name").AsString())) |> dict
    Some tankNames
  with
  | :? System.Exception as e -> 
    printfn "getTanksNames exception %A" e
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
    | :? System.Exception as e -> 
      printfn "getPlayerTansk exception %A" e
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
    | :? System.Exception as e -> None
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
    | :? System.Exception as e -> None
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
