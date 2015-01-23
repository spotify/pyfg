@Grab(group='com.spotify', module='pipeline-conventions', version='1.0.2')
import com.spotify.pipeline.Pipeline

new Pipeline(this) {{ build {
  notify.byMail(recipients: 'as43650@spotify.com')
  group(name: 'Test') {
    shell.run(cmd: "/spotify/virtualenv/bin/pip install -r \$WORKSPACE/requirements.txt ; cd \$WORKSPACE;/spotify/virtualenv/bin/nosetests")
  }
  group(name: 'PyPi Upload') {
    shell.run(cmd: "python setup.py sdist; scp -i /spotify/buildagent/.ssh/id_rsa -o StrictHostKeyChecking=no dist/*.tar.gz spotify-pypiserver@pypi.spotify.net:/var/lib/pypiserver/")
  }
}}}

