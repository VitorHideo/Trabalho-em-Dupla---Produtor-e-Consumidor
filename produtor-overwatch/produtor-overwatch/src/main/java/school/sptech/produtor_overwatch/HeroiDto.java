package school.sptech.produtor_overwatch;

public class HeroiDto {

    private String nome;
    private int idade;
    private String funcao;
    private String fraseUlt;

    public HeroiDto() {
    }

    public HeroiDto(String nome, int idade, String funcao, String fraseUlt) {
        this.nome = nome;
        this.idade = idade;
        this.funcao = funcao;
        this.fraseUlt = fraseUlt;
    }

    public String getNome() {
        return nome;
    }

    public void setNome(String nome) {
        this.nome = nome;
    }

    public int getIdade() {
        return idade;
    }

    public void setIdade(int idade) {
        this.idade = idade;
    }

    public String getFuncao() {
        return funcao;
    }

    public void setFuncao(String funcao) {
        this.funcao = funcao;
    }

    public String getFraseUlt() {
        return fraseUlt;
    }

    public void setFraseUlt(String fraseUlt) {
        this.fraseUlt = fraseUlt;
    }
}
