package school.sptech.produtor_overwatch;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;

@RestController
@RequestMapping("/herois")
@Tag(name = "Heróis", description = "Endpoints para envio de heróis à fila RabbitMQ")
public class HeroiController {

    private final HeroiProducer producer;

    public HeroiController(HeroiProducer producer) {
        this.producer = producer;
    }

    @PostMapping
    @Operation(summary = "Envia um herói", description = "Publica um herói na fila RabbitMQ configurada.")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "Herói enviado com sucesso")
    })
    public ResponseEntity<String> enviarHeroi(@RequestBody HeroiDto heroi) {
        producer.sendMessage(heroi);
        return ResponseEntity.ok("Herói enviado para a fila: " + heroi.getNome());
    }
}
