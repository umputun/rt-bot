package ru.hixon

import com.fasterxml.jackson.module.kotlin.KotlinModule
import org.springframework.boot.SpringApplication
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.context.annotation.Bean
import org.springframework.http.converter.json.Jackson2ObjectMapperBuilder

@SpringBootApplication
open class Application {

    @Bean
    open fun objectMapperBuilder(): Jackson2ObjectMapperBuilder
            = Jackson2ObjectMapperBuilder().modulesToInstall(KotlinModule())
            .featuresToEnable(com.fasterxml.jackson.core.JsonParser.Feature.ALLOW_SINGLE_QUOTES)


    companion object {
        @JvmStatic fun main(args: Array<String>) {
            SpringApplication.run(Application::class.java, *args)
        }
    }
}