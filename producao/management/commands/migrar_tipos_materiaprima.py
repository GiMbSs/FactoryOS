from django.core.management.base import BaseCommand
from django.db import transaction
from producao.models import MateriaPrima, TipoMateriaPrima


class Command(BaseCommand):
    help = 'Migra tipos antigos de matéria-prima para o novo modelo TipoMateriaPrima'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Iniciando migração dos tipos de matéria-prima...'))
        
        # Mapeamento dos tipos antigos para novos
        mapeamento_tipos = {
            'MADEIRA_BRUTA': {'nome': 'Madeira Bruta', 'icone': 'bi-tree', 'cor': 'success'},
            'VARETA_MADEIRA': {'nome': 'Vareta de Madeira', 'icone': 'bi-rulers', 'cor': 'success'},
            'TECIDO_MALHA': {'nome': 'Tecido Malha', 'icone': 'bi-basket', 'cor': 'info'},
            'TECIDO_PANO_CRU': {'nome': 'Tecido Pano Cru', 'icone': 'bi-basket', 'cor': 'info'},
            'CABO_PLASTICO': {'nome': 'Cabo Plástico', 'icone': 'bi-box', 'cor': 'warning'},
        }
        
        try:
            with transaction.atomic():
                tipos_criados = {}
                
                # Para cada tipo antigo, cria um novo tipo
                for tipo_key, tipo_data in mapeamento_tipos.items():
                    novo_tipo, criado = TipoMateriaPrima.objects.get_or_create(
                        nome=tipo_data['nome'],
                        defaults={
                            'icone': tipo_data['icone'],
                            'cor': tipo_data['cor'],
                            'descricao': f'Migrado automaticamente do tipo antigo: {tipo_key}'
                        }
                    )
                    
                    if criado:
                        self.stdout.write(self.style.SUCCESS(f'Criado novo tipo: {novo_tipo.nome}'))
                    else:
                        self.stdout.write(self.style.NOTICE(f'Tipo já existente: {novo_tipo.nome}'))
                        
                    tipos_criados[tipo_key] = novo_tipo
                
                # Atualiza todas as matérias-primas para usar os novos tipos
                count = 0
                for material in MateriaPrima.objects.filter(tipo_materia_prima__isnull=True):
                    if material.tipo in tipos_criados:
                        material.tipo_materia_prima = tipos_criados[material.tipo]
                        material.save(update_fields=['tipo_materia_prima'])
                        count += 1
                
                self.stdout.write(self.style.SUCCESS(f'Migração concluída! {len(tipos_criados)} tipos criados e {count} matérias-primas atualizadas.'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao migrar tipos de matéria-prima: {e}'))