package school.sptech.produtor_overwatch;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/herois")
public class HeroiController {

    private final HeroiProducer producer;

    public HeroiController(HeroiProducer producer) {
        this.producer = producer;
    }

    @PostMapping
    public ResponseEntity<String> enviarHeroi(@RequestBody HeroiDto heroi) {
        producer.sendMessage(heroi);
        return ResponseEntity.ok("Herói enviado para a fila: " + heroi.getNome());
    }
}
