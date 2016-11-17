use Mojolicious::Lite;
use JSON;
use lib './lib';

use StatBot;

helper bot => sub { state $bot = StatBot->new };

our $BOT_NAME_ID = 'stat-bot';

post '/event' => sub {
    my $c = shift;

    my $data = {};

    eval {
        $data = from_json( $c->req->body, { 'utf8' => 1 } ) || {};
    };

    my $response = $c->bot->sb_catch_action( $data );
    if ( $response ) {
        $c->render(
            status => 201,
            json    => {
                text    => $response,
                bot     => $BOT_NAME_ID,
            }
        );
    } else {
        $c->render(
            status  => 417,
            text    => '',
        );
    }

};

get '/info' => sub {
    my $c = shift;
    $c->render(
        status => 200,
        json    => {
            'author'    => 'Roman L, http://twitter/roman_tic',
            'info'      => 'Бот stat-bot считает статистику слов и сообщений. Может сказать кто самый болтливый в чате и какие слова (по частям речи) чаще всего употребляют.',
            'commands'  => [
                'Кто сегодня болтун? - Самый болтливый пользователь за сегодняшний день',
                'Топ болтунов сегодня - Топ самых болтливых пользоватлеей сегодня',
                'О чем говорили? - Самые популярные слова-существительный в чате',
                'Как в целом? - Эмоциональная окраска беседы из пяти самых популярных прилагательных',
                'А что делать? - Подборка из пяти самых популярных глаголов в чате за сегодня',
                'Сколько раз употребили слово бобук? - Ну, тут всё и так понятно...',
            ],
        }
    );
};

app->start('daemon', '-l', 'http://*:8080');