from django.core.management.base import BaseCommand
from assistant.ai import get_store
class Command(BaseCommand):
    help = 'Print indexed metadata count and sample'
    def handle(self, *args, **options):
        store = get_store()
        self.stdout.write(f'Index contains {len(store.metadatas)} entries')
        if store.metadatas:
            self.stdout.write('Sample:')
            self.stdout.write(str(store.metadatas[0]))
