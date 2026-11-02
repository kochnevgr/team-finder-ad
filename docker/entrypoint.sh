#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

case "${LOAD_TEST_DATA:-False}" in
    True|true|1|yes)
        python manage.py load_test_data
        ;;
esac

exec gunicorn team_finder.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --access-logfile - \
    --error-logfile -
