package school.sptech.produtor_overwatch;

import org.springframework.amqp.core.Queue;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMQConfig {

    public static final String HEROI_QUEUE = "overwatch_herois";

    @Bean
    public Queue queue() {
        return new Queue(HEROI_QUEUE, false);
    }
}
