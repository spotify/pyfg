@Grab(group='com.spotify', module='pipeline-conventions', version='1.0.2')
import com.spotify.pipeline.Pipeline

new Pipeline(this) {{ build {
  notify.byMail(recipients: 'as43650@spotify.com')
  group(name: 'Test') {
    shell.run(cmd: "nosetests")
  }
}}}

