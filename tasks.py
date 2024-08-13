from robocorp.tasks import task
import main


@task
def minimal_task():
    main.management_path()
    main.define_logger()
    main.main()
