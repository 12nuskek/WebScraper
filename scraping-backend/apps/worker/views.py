from django.shortcuts import render

# Worker app doesn't need API views - it runs as a management command
# All functionality is handled through the run_worker management command