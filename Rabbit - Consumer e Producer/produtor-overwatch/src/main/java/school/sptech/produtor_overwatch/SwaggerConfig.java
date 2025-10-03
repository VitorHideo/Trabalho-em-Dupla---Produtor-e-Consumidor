package school.sptech.produtor_overwatch;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.Contact;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SwaggerConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Produtor Overwatch API")
                        .version("1.0.0")
                        .description("API para envio de heróis do Overwatch para fila RabbitMQ")
                        .contact(new Contact()
                                .name("SPTech")
                                .email("contato@sptech.school")));
    }
}
