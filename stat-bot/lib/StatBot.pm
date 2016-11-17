package StatBot;

use strict;
use warnings;
use JSON;
use utf8;
use Encode;
use Digest::MD5 qw/md5_hex/;

my $NAMES = {};
my $MYSTEM_PATH = '';
my $CUT = 5;
my $SECRET = 'e615d5f8426a238ea8b15445c9ce8fea';

my $BABBLERS = {
    'total' => {},
};
my $WORDS = {
    'total' => {},
};

sub new {
    my $instance = shift;
    my $class = ref($instance) || $instance;

    my $self = {
        @_,
        'last_action_time'  => time(),
        'buffer'            => [],
    };

    bless($self, $class);
    return $self->init;
}

sub init {
    my $self = shift;

    if ( $^O =~ /Win/ ) {
        $MYSTEM_PATH = 'mystem';
    }
    else {
        $MYSTEM_PATH = '/stat-bot/mystem';
    }

    $BABBLERS = {
        'total' => {},
    };
    $WORDS = {
        'total' => {},
    };
    $self->{'buffer'} = [];

    return $self;
}

sub last_action_time {
    my $self = shift;

    my $last = $self->{'last_action_time'};
    if ( @_ ) {
        $self->{'last_action_time'} = shift;
    }

    return $last;
}

sub hello {
    my $self = shift;
    return 'Привет! Меня зовут stat-bot v 0.1 и я слежу за вашим базаром!';
}

sub sb_catch_action {
    my $self = shift;
    my $data = shift || '';
    my $r = '';

    my $text = $data->{'text'} || '';
    $text =~ s/\s+?/ /gsm;
    $text =~ tr/А-Я/а-я/;
    $text =~ tr/A-Z/a-z/;

    if ( $text ) {
        my $last_time = $self->last_action_time( time() );

        if ( $text =~ /кто.+?болтун/ ) {
            $r = $self->sb_who_is_babbler( $text =~ /сегодня/ );
        }
        elsif ( $text =~ /топ болтунов/ ) {
            $r = $self->sb_babblers_top( $text =~ /сегодня/ );
        }
        elsif ( $text =~ /о ч(е|ё)м.+?говорили/ ) {
            $r = $self->sb_topic_top( 'S' );
        }
        elsif ( $text =~ /как в целом/ ) {
            $r = $self->sb_topic_top( 'A' );
        }
        elsif ( $text =~ /а что делать/ ) {
            $r = $self->sb_topic_top( 'V' );
        }
        elsif ( $text =~ /сколько раз.+?слово (.+?)\?/ ) {
            $r = $self->sb_count_word( $1 );
        }
        elsif ( $text =~ /давайте познакомимся/ ) {
            $r = $self->sb_hello;
        }
        elsif ( $data->{'action'} ) {
            if ( $self->check_rights( $data ) ) {
                if ( $data->{'action'} eq 'configure' ) {
                    $self->sb_configure( $data );
                }
                if ( $data->{'action'} eq 'reset' ) {
                    $self->init;
                }
                elsif ( $data->{'action'} eq 'internals' ) {
                    $r = $self->sb_internals;
                }
            }
        }
        else {
            $self->update_stat( $data );
            $self->flush_debug_data;
            #$r = $text;
        }

    }

    return $r;
}

sub check_rights {
    my $self = shift;
    my $data = shift || {};
    my $is = 0;

    if ( $data->{'secret'} ) {
        if ( md5_hex( $data->{'secret'} ) eq $SECRET ) {
            $is = 1;
        }
    }

    return $is;
}

sub get_active_day {
    my $self = shift;

    my @t = localtime( time() );
    my $day = $t[3];

    unless ( exists $BABBLERS->{$day} ) {
        $BABBLERS = {
            'total' => $BABBLERS->{'total'},
            $day    => {}
        };

        $WORDS = {
            'total' => $WORDS->{'total'},
            $day    => {}
        };
    }

    return $day;
}

sub push_text {
    my $self = shift;
    my $text = shift || '';

    push @{$self->{'buffer'}}, $text;

    return $self;
}

sub process_line_buffer {
    my $self = shift;

    return $self unless ( @{$self->{'buffer'}} );

    my $active_day = $self->get_active_day;

    my $fp;
    my $fname = rand(100).'.tmp';
    open( $fp, ">:encoding(UTF-8)", $fname );
    print $fp join( "\n", @{$self->{'buffer'}} );
    close( $fp );

    my $out = `$MYSTEM_PATH -e utf-8 -nli $fname`;
    my @buffer = split( /\n/, decode_utf8( $out ) );
    foreach ( @buffer ) {
        my @var = split( /,/, $_);
        @var = split( /\|/, $var[0] );
        if ( $var[0] =~ /^(.+?)\=(S|A|V)(\=|$)/ ) {
            my $word = $1;
            my $ps = $2;
            $word =~ s/\?//g;
            if ( length( $word ) > 3 ) {
                $WORDS->{'total'}->{ $ps }->{ $word } ++;
                $WORDS->{ $active_day }->{ $ps }->{ $word } ++;
            }
        }
    }
    unlink $fname;

    $self->{'buffer'} = [];

    return $self;
}

sub update_stat {
    my $self = shift;
    my $data = shift || {};

    my $active_day = $self->get_active_day;

    $NAMES->{ $data->{'username'} } = $data->{'display_name'};

    $BABBLERS->{'total'}->{ $data->{'username'} } ++;
    $BABBLERS->{ $active_day }->{ $data->{'username'} } ++;

    $self->push_text( $data->{'text'} || '' );

    return $self;
}

sub get_babblers_top {
    my $self = shift;
    my $is_today = shift || 0;

    my $target = 'total';
    if ( $is_today ) {
        $target = $self->get_active_day;
    }

    my $target_map = $BABBLERS->{$target} || {};
    return sort { $target_map->{$b} <=> $target_map->{$a} } keys( %{$target_map} );
}

sub sb_who_is_babbler {
    my $self = shift;
    my $is_today = shift || 0;
    my $r = 'И покойники с косами стоять, и тишинаааа...';

    my @ext = (
        'самый болтун в этом чатике!',
        'шалунишка-болтунишка!',
        'болтает и болтает!',
    );

    my @top = $self->get_babblers_top( $is_today );
    if ( @top ) {
        my $who = shift @top;
        $r = $NAMES->{$who}.' - '.$ext[rand(@ext)];
    }

    return $r;
}

sub sb_babblers_top {
    my $self = shift;
    my $is_today = shift || 0;
    my $r = 'И покойники с косами стоять, и тишинаааа...';

    my @ext = (
        'Болтуны: ',
        'Говоруны вы наши: ',
        'Ой, всё, болтуны: ',
    );

    my @top = $self->get_babblers_top( $is_today );
    if ( @top ) {
        $r = $ext[rand(@ext)].join( ', ', map { $NAMES->{$_} } grep { defined($_) } @top[0..$CUT-1] );
    }

    return $r;
}

sub sb_topic_top {
    my $self = shift;
    my $type = shift;
    my $r = '';

    my $R = {
        'S'     => 'Чот молчат все...',
        'A'     => 'Печально (((',
        'V'     => 'Никто ничего не хочет, обленились все'
    };

    $r = $R->{$type};

    $self->process_line_buffer;

    my $target = $self->get_active_day;

    my @ext = (
        'Топ слов: ',
        'Сегодня популярно: ',
    );

    my $target_map = $WORDS->{$target}->{$type} || {};
    my @top = sort { $target_map->{$b} <=> $target_map->{$a} } keys( %{$target_map} );
    if ( @top ) {
        $r = $ext[rand(@ext)].join( ', ', map { $_.' ('.$target_map->{$_}.')' } grep { defined($_) } @top[0..$CUT-1] );
    }

    return $r;
}

sub sb_count_word {
    my $self = shift;
    my $word = shift || '';
    my $r = 'Чот незнаю слова '.$word.' ((( Я считаю только существительные...';

    $self->process_line_buffer;
    my $target = $self->get_active_day;
    if ( $WORDS->{$target}->{'S'}->{$word} ) {
        my $c = $WORDS->{$target}->{'S'}->{$word};
        $word =~ tr/а-я/А-Я/;
        $word =~ tr/a-z/A-Z/;
        $r = qq{Слово $word употребили $c раз в разных позах и вариациях.};
    }

    return $r;
}

sub sb_internals {
    my $self = shift;
    return {
        'bubblers'  => $BABBLERS,
        'words'     => $WORDS,
        'lines'     => $self->{'buffer'}
    }
}

sub sb_configure {
    my $self = shift;
    my $data = shift || {};

    $CUT = $data->{'cut'} || $CUT;

    return $self;
}

sub flush_debug_data {
    my $self = shift;

    my $debug;
    open( $debug, ">:encoding(UTF-8)", "debug.json" );
    print $debug to_json( { 'bubblers' => $BABBLERS, 'words' => $WORDS }, { 'pretty' => 1 } );
    close( $debug );

    return $self;
}

1;