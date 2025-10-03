package school.sptech.produtor_overwatch;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Service;

@Service
public class HeroiProducer {

    private final RabbitTemplate rabbitTemplate;
    private final ObjectMapper objectMapper;

    public HeroiProducer(RabbitTemplate rabbitTemplate, ObjectMapper objectMapper) {
        this.rabbitTemplate = rabbitTemplate;
        this.objectMapper = objectMapper;
    }

    public void sendMessage(HeroiDto heroi) {
        try {
            String jsonMessage = objectMapper.writeValueAsString(heroi);
            rabbitTemplate.convertAndSend(RabbitMQConfig.HEROI_QUEUE, jsonMessage);
            System.out.println("Mensagem enviada: " + jsonMessage);
        } catch (JsonProcessingException e) {
            e.printStackTrace();
        }
    }
}
