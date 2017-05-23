uid = ENV['UID']&.to_i

`chown -R #{uid}:#{uid} /app` if uid
Process.uid = uid || (Process::UID.from_name 'nobody')

exec 'rackup'
