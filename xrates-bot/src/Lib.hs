{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}

module Lib
    ( libMain
    ) where

import Control.Concurrent
import Control.Concurrent.STM
import Control.Concurrent.STM.TMVar
import Control.Exception
import Control.Lens
import Control.Monad
import Control.Monad.IO.Class
import Data.Aeson
import Data.Aeson.Lens
import Data.Array
import Data.Maybe
import Data.Monoid
import Data.Ratio
import Data.Time
import Network.HTTP.Client (newManager, parseRequest, httpLbs, HttpException)
import Network.HTTP.Client.TLS (tlsManagerSettings)
import Network.HTTP.Simple (getResponseStatusCode, getResponseBody)
import Network.HTTP.Types
import Text.Regex
import Text.Regex.Base
import Web.Scotty
import qualified Data.ByteString.Lazy.Char8 as LB
import qualified Data.ByteString.Lazy.UTF8 as LUTF8
import qualified Data.Map as Map
import qualified Data.Text as T
import qualified Data.Text.Lazy as LT
import qualified Data.Text.Read as T


botID = "xrates"
botInfo = botID <> " TODO"


rubSynonyms = ["RUB", "rubls", "rubl", "рублей", "рубля", "рубль", "руб", "руб.", "р.", "рублях", "₽"]
usdSynonyms = ["USD", "dollars", "dollar", "долларов", "доллара", "доллар", "долларах", "$"]
eurSynonyms = ["EUR", "euros", "euro", "евро", "€"]
uahSynonyms = ["UAH", "hryvnias", "hryvnia", "гривен", "гривны", "гривна", "гривнах", "₴"]

currencySynonyms :: Map.Map T.Text T.Text
currencySynonyms = Map.fromList (concat $ map (\v -> zip v $ take (length v) (repeat $ head v)) [rubSynonyms, usdSynonyms, eurSynonyms, uahSynonyms])


threadDelayInSec :: Int -> IO ()
threadDelayInSec sec = threadDelay $ 1000000 * sec


fetchXrates :: IO (Map.Map T.Text Double)
fetchXrates = catch fetch $ \(_ :: HttpException) -> return Map.empty
    where
        fetch = do
            request <- parseRequest "https://www.cbr-xml-daily.ru/daily_jsonp.js"
            response <- httpLbs request =<< newManager tlsManagerSettings
            case getResponseStatusCode response of
                200 -> do
                    let r = mkRegex "^.+CBR_XML_Daily_Ru\\((.+)\\);$"
                    let result = parse . LB.pack . fst . flip (!) 1 . head . matchAllText r . LB.unpack $ getResponseBody response
                    return $ Map.insert "RUB" 1.0 result
                _   -> return Map.empty

        parse :: LB.ByteString -> Map.Map T.Text Double
        parse json = Map.fromList . catMaybes $ map convert (decode json ^. key "Valute" ^.. traverseObject)

        convert :: Maybe Value -> Maybe (T.Text, Double)
        convert v = do
            charCode <- v ^. key "CharCode" . asText
            value <- v ^. key "Value" . asDouble
            return (charCode, value)


fetcher :: TMVar (Map.Map T.Text Double) -> IO ()
fetcher xratesVar = do
    xrates <- fetchXrates
    print xrates
    -- wait for a minute in case of fetch issues
    if Map.null xrates then threadDelayInSec 1
    -- normally update xrates once per a day at 5 a.m.
    else do
        atomically $ do
            isEmpty <- isEmptyTMVar xratesVar
            case isEmpty of
                True  -> putTMVar xratesVar xrates
                False -> swapTMVar xratesVar xrates >> return ()
        now <- getCurrentTime
        let tomorrow = UTCTime (addDays 1 $ utctDay now) (fromIntegral $ 5 * 3600)
        threadDelayInSec . floor $ diffUTCTime tomorrow now
    fetcher xratesVar


libMain :: IO ()
libMain = do
    xrates <- atomically $ newEmptyTMVar
    forkIO $ fetcher xrates
    scotty 8080 $ routes xrates


routes :: TMVar (Map.Map T.Text Double) -> ScottyM ()
routes xrates = do
    post "/event" $ postEvent xrates
    get "/info" getInfo


postEvent :: TMVar (Map.Map T.Text Double) -> ActionM ()
postEvent xratesVar = do
    text <- view (key "text" . asText) . Just <$> jsonData
    xrates <- liftIO . atomically $ readTMVar xratesVar
    case doEvent xrates text of
        Just message -> do
            Web.Scotty.json (decode . LUTF8.fromString $ "{\"bot\":\"" <> botID <>  "\",\"text\":\"" <> T.unpack message <> "\"}" :: Maybe Value)
            status created201
        _            -> status expectationFailed417
    --
    where
        doEvent :: Map.Map T.Text Double -> Maybe T.Text -> Maybe T.Text
        doEvent xrates request = do
            (countText, from, to) <- parse =<< request
            count <- Just . fst =<< (either (const Nothing) Just $ T.double countText)
            rateFrom <- Map.lookup (toCode from) xrates
            rateTo <- Map.lookup (toCode to) xrates
            Just $ T.pack (show count <> " " <> T.unpack (toCode from) <> " = " <> show (count * rateFrom / rateTo) <> " " <> T.unpack (toCode to))

        parse :: T.Text -> Maybe (T.Text, T.Text, T.Text)
        parse request = do
            let r = mkRegex "^([0-9\\.,]+) ([^ ]+) (в|in) (.+)$"
            case matchAllText r $ T.unpack request of
                [result] -> Just (T.pack . fst $ result ! 1, T.pack . fst $ result ! 2, T.pack . fst $ result ! 4)
                _        -> Nothing

        toCode :: T.Text -> T.Text
        toCode v = case Map.lookup (T.toLower v) currencySynonyms of
            Just code -> code
            Nothing   -> T.toUpper v


getInfo :: ActionM ()
getInfo = Web.Scotty.json (decode . LUTF8.fromString $ "{\"author\":\"ssgreg\",\"info\":\"" <> botInfo <>  "\"}" :: Maybe Value)
