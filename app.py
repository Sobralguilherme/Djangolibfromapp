from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from datetime import datetime
import logging

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

# Função para carregar livros a partir do Excel
def carregar_livros():
    try:
        df = pd.read_excel('livros.xlsx')
        logging.debug(f"Colunas do Excel: {df.columns.tolist()}")
        logging.debug(f"Primeiras linhas do DataFrame:\n{df.head()}")
        livros = df.to_dict(orient='records')
        logging.debug(f"Livros carregados: {livros}")
        logging.info("Livros carregados com sucesso.")
    except FileNotFoundError:
        livros = []
        logging.error("Arquivo livros.xlsx não encontrado.")
    except Exception as e:
        livros = []
        logging.error(f"Erro ao carregar livros: {e}")
    return livros

@app.route('/')
def index():
    try:
        livros = carregar_livros()
        logging.debug(f"Livros enviados para o template: {livros}")
        if not livros:
            logging.warning("Nenhum livro encontrado.")
        return render_template('index.html', livros=livros)
    except Exception as e:
        logging.error(f"Erro ao renderizar a página inicial: {e}")
        return "Ocorreu um erro ao carregar a página inicial.", 500

@app.route('/reservar', methods=['POST'])
def reservar():
    try:
        aluno = request.form['aluno']
        livro_selecionado = request.form['livro']
        livros = carregar_livros()
        livro_info = next((livro for livro in livros if livro["Nome"] == livro_selecionado), None)

        if not livro_info:
            logging.warning(f"Livro {livro_selecionado} não encontrado.")
            return redirect(url_for('index'))

        # Carregar dados existentes ou criar novo DataFrame
        try:
            df = pd.read_excel('reservas.xlsx')
        except FileNotFoundError:
            df = pd.DataFrame(columns=['Data', 'Aluno', 'Livro', 'Autor'])
            logging.info("Criado novo arquivo reservas.xlsx.")

        # Adicionar nova reserva
        nova_reserva = {
            'Data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Aluno': aluno,
            'Livro': livro_info['Nome'],
            'Autor': livro_info['Autor']
        }
        df = df.append(nova_reserva, ignore_index=True)

        # Salvar no Excel
        df.to_excel('reservas.xlsx', index=False)
        logging.info(f"Reserva adicionada: {nova_reserva}")

        return redirect(url_for('index'))
    except Exception as e:
        logging.error(f"Erro ao processar reserva: sta{e}")
        return "Ocorreu um erro ao processar a reserva.", 500

if __name__ == '__main__':
    app.run(debug=True)
