from invoke import task


@task
def lock(ctx, env='local', upgrade=False):
    """Lock dependencies

    Lock *.in files to populate *.txt file with frozen versions
    """
    upgrade_str = ''

    if upgrade:
        upgrade_str = '-U'

    ctx.run(
        'pip-compile {upgrade_str} requirements/common.in '
        'requirements/{env}.in --output-file requirements/{env}.txt'.format(
            env=env, upgrade_str=upgrade_str
        )
    )


@task
def install(ctx, env='local'):
    """Install dependencies

    Install dependencies from *.txt file
    """

    ctx.run('pip install -r requirements/{env}.txt'.format(env=env))
