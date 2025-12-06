document.addEventListener('DOMContentLoaded', function() {
    
    // Procura o campo de CEP pelo ID padrão do Django (id_cep)
    const cepInput = document.getElementById('id_cep');
    
    if (cepInput) {
        cepInput.addEventListener('blur', function() {
            // Remove caracteres não numéricos
            const cep = this.value.replace(/\D/g, '');

            // Verifica se o CEP tem 8 dígitos
            if (cep.length === 8) {
                // Faz a busca na API do ViaCEP
                fetch(`https://viacep.com.br/ws/${cep}/json/`)
                    .then(response => response.json())
                    .then(data => {
                        if (!data.erro) {
                            // Preenche os campos automaticamente
                            // O '?' verifica se o campo existe antes de tentar preencher
                            document.getElementById('id_logradouro')?.setAttribute('value', data.logradouro);
                            document.getElementById('id_bairro')?.setAttribute('value', data.bairro);
                            document.getElementById('id_cidade')?.setAttribute('value', data.localidade);
                            document.getElementById('id_uf')?.setAttribute('value', data.uf);
                            
                            // Se estiver usando inputs manuais (value direto), use esta forma:
                            if(document.getElementById('id_logradouro')) document.getElementById('id_logradouro').value = data.logradouro;
                            if(document.getElementById('id_bairro')) document.getElementById('id_bairro').value = data.bairro;
                            if(document.getElementById('id_cidade')) document.getElementById('id_cidade').value = data.localidade;
                            if(document.getElementById('id_uf')) document.getElementById('id_uf').value = data.uf;

                            // Coloca o foco no campo de número para o usuário digitar
                            document.getElementById('id_numero')?.focus();
                        } else {
                            alert("CEP não encontrado.");
                        }
                    })
                    .catch(error => console.error('Erro ao buscar CEP:', error));
            }
        });
    }
});