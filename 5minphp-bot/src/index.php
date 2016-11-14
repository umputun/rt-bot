<?php
define('LOCAL_FILE', __DIR__ . '/phpfact.txt');
define('REMOTE_FILE', 'https://raw.githubusercontent.com/pqr/5minphp-bot/master/phpfact.txt');
define('BOT_NAME', 'Пятиминутка PHP');

if (isset($_SERVER['REQUEST_URI']) && $_SERVER['REQUEST_URI'] === '/info') {
    http_response_code(200);
    print json_encode([
        'author' => 'Пётр Мязин (twitter: PetrMyazin)',
        'info' => 'Если в чате упоминается PHP, то "Пятиминутка PHP" сообщает какой-то интересный и полезный факт об этом языке программирования! База знаний постоянно пополняется!',
        'commands' => ["php"]
    ]);
    exit();
}

$input = file_get_contents('php://input');
if (!$input) {
    http_response_code(417);
    exit();
}

$inputData = json_decode($input, true);
if (!$inputData || !isset($inputData['text']) || !is_string($inputData['text'])) {
    http_response_code(417);
    exit();
}

$username = $inputData['username'] ?? '';
$displayname = $inputData['display_name'] ?? '';
if ($username === BOT_NAME
    || $displayname === BOT_NAME
    || $username === 'rt-bot'
    || $displayname === 'rt-bot'
    || mb_stripos($inputData['text'], BOT_NAME) !== false) {

    // without test chat it's not clear yet how messagees from the bot will look like
    // so trying to check all possible conditions to prevent reply on self messages
    http_response_code(417);
    exit();
}

if (mb_stripos($inputData['text'], 'пятиминутка обновись') !== false) {
    http_response_code(201);
    print json_encode(['text' => 'У меня для вас есть свежие факты про PHP...', 'bot' => BOT_NAME]);
    exit();
}

if (!hasWordPhp($inputData['text'])) {
    http_response_code(417);
    exit();
}

$fact = getRandomFact($inputData['text']);
if (!$fact) {
    http_response_code(417);
    exit();
}


http_response_code(201);
print json_encode(['text' => $fact, 'bot' => BOT_NAME]);

function hasWordPhp($inputText): bool
{
    $words = preg_split('/\s/', mb_strtolower($inputText, 'UTF-8'));
    foreach ($words as $word) {
        if ($word === 'php' || $word === 'пхп') {
            return true;
        }
    }

    return false;
}


function getRandomFact(string $inputData): string
{
    if (!file_exists(LOCAL_FILE) || time() - @filemtime(LOCAL_FILE) > 3600) {
        downloadFacts();
    }

    $allFacts = @file(LOCAL_FILE, FILE_IGNORE_NEW_LINES);
    if (!$allFacts) {
        return '';
    }

    $allFacts = array_filter($allFacts);
    if (!$allFacts) {
        return '';
    }

    return $allFacts[random_int(0, count($allFacts) - 1)];
}

function downloadFacts()
{
    $newFacts = @file_get_contents(REMOTE_FILE);
    if ($newFacts) {
        @file_put_contents(LOCAL_FILE, $newFacts);
    }
}
