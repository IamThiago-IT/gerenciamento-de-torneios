#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <algorithm>
#include <random>

using namespace std;

// ========== ENUMS ==========

enum TipoJogador { AMADOR, PROFISSIONAL };
enum ModalidadeTorneio { MATA_MATA, PONTOS_CORRIDOS };

// ========== CLASSE JOGADOR ==========

class Jogador {
private:
    string nome;
    int idade;
    string esporte;
    TipoJogador tipo;
    int vitorias = 0;
    int derrotas = 0;
    int empates = 0;

public:
    Jogador(string n, int i, string e, TipoJogador t)
        : nome(n), idade(i), esporte(e), tipo(t) {}

    string getNome() const { return nome; }
    int getVitorias() const { return vitorias; }

    void registrarVitoria() { vitorias++; }
    void registrarDerrota() { derrotas++; }
    void registrarEmpate() { empates++; }

    string getEstatisticas() const {
        return nome + " | V:" + to_string(vitorias) +
               " D:" + to_string(derrotas) +
               " E:" + to_string(empates);
    }

    void salvar(ofstream &out) {
        out << nome << "," << idade << "," << esporte << ","
            << tipo << "," << vitorias << "," << derrotas << "," << empates << endl;
    }

    static Jogador carregar(string linha) {
        stringstream ss(linha);
        string nome, esporte;
        int idade, tipo, v, d, e;
        getline(ss, nome, ',');
        ss >> idade; ss.ignore();
        getline(ss, esporte, ',');
        ss >> tipo; ss.ignore();
        ss >> v; ss.ignore();
        ss >> d; ss.ignore();
        ss >> e;
        Jogador j(nome, idade, esporte, (TipoJogador)tipo);
        while(v--) j.registrarVitoria();
        while(d--) j.registrarDerrota();
        while(e--) j.registrarEmpate();
        return j;
    }
};

// ========== CLASSE EQUIPE ==========

class Equipe {
private:
    string nome;
    vector<Jogador> jogadores;

public:
    Equipe(string n) : nome(n) {}

    void adicionarJogador(Jogador j) { jogadores.push_back(j); }

    string getNome() const { return nome; }

    void listarJogadores() const {
        cout << "Equipe: " << nome << endl;
        for (auto &j : jogadores)
            cout << " - " << j.getEstatisticas() << endl;
    }
};

// ========== CLASSE RESULTADO / PARTIDA ==========

struct Resultado {
    int placar1;
    int placar2;
};

class Partida {
private:
    string participante1;
    string participante2;
    Resultado resultado;

public:
    Partida(string p1, string p2) : participante1(p1), participante2(p2) {}

    void simularResultado() {
        random_device rd;
        mt19937 gen(rd());
        uniform_int_distribution<> dis(0, 5);
        resultado.placar1 = dis(gen);
        resultado.placar2 = dis(gen);
    }

    void exibir() {
        cout << participante1 << " " << resultado.placar1
             << " x " << resultado.placar2
             << " " << participante2 << endl;
    }
};

// ========== CLASSE TORNEIO ==========

class Torneio {
private:
    string nome;
    ModalidadeTorneio modalidade;
    vector<string> participantes;
    vector<Partida> partidas;

public:
    Torneio(string n, ModalidadeTorneio m) : nome(n), modalidade(m) {}

    void adicionarParticipante(string p) { participantes.push_back(p); }

    void gerarRodadas() {
        for (size_t i = 0; i < participantes.size(); i += 2) {
            if (i + 1 < participantes.size()) {
                partidas.emplace_back(participantes[i], participantes[i + 1]);
            }
        }
        cout << "Rodadas geradas com sucesso!" << endl;
    }

    void simularPartidas() {
        for (auto &p : partidas) {
            p.simularResultado();
            p.exibir();
        }
    }
};

// ========== CLASSE RANKING ==========

class Ranking {
private:
    vector<pair<string, int>> classificacao;

public:
    void adicionarPontuacao(string nome, int pontos) {
        classificacao.emplace_back(nome, pontos);
    }

    void gerar() {
        sort(classificacao.begin(), classificacao.end(),
             [](auto &a, auto &b) { return a.second > b.second; });
    }

    void exibir() {
        cout << "\n=== Ranking Final ===" << endl;
        for (auto &r : classificacao)
            cout << r.first << " - " << r.second << " pts" << endl;
    }

    void exportar(string arquivo) {
        ofstream out(arquivo);
        for (auto &r : classificacao)
            out << r.first << "," << r.second << endl;
        out.close();
        cout << "Ranking exportado para " << arquivo << endl;
    }
};

// ========== CLASSE DE PERSISTÊNCIA ==========

class Persistencia {
public:
    static void salvarJogadores(vector<Jogador> jogadores, string arquivo) {
        ofstream out(arquivo);
        for (auto &j : jogadores)
            j.salvar(out);
        out.close();
    }
};

// ========== MAIN ==========

int main() {
    cout << "=== Sistema de Gerenciamento de Torneios ===" << endl;

    // Cadastro de jogadores
    Jogador j1("Ana", 22, "Futebol", PROFISSIONAL);
    Jogador j2("Carlos", 25, "Futebol", AMADOR);

    vector<Jogador> jogadores = {j1, j2};

    // Criar equipe
    Equipe equipe1("Time A");
    equipe1.adicionarJogador(j1);
    equipe1.adicionarJogador(j2);
    equipe1.listarJogadores();

    // Criar torneio
    Torneio t("Copa da Amizade", PONTOS_CORRIDOS);
    t.adicionarParticipante("Ana");
    t.adicionarParticipante("Carlos");
    t.gerarRodadas();
    t.simularPartidas();

    // Ranking
    Ranking r;
    r.adicionarPontuacao("Ana", 3);
    r.adicionarPontuacao("Carlos", 1);
    r.gerar();
    r.exibir();
    r.exportar("ranking.csv");

    // Persistência
    Persistencia::salvarJogadores(jogadores, "jogadores.csv");

    cout << "\nEncerrando sistema..." << endl;
    return 0;
}
