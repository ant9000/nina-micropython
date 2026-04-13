add_library(usermod_nfr_oberon INTERFACE)

target_sources(usermod_nfr_oberon INTERFACE
  ${CMAKE_CURRENT_LIST_DIR}/nrf_oberon.c
)

target_include_directories(usermod_nfr_oberon INTERFACE
  ${CMAKE_CURRENT_LIST_DIR}/include
)

target_link_libraries(usermod INTERFACE usermod_nfr_oberon)

add_library(liboberon STATIC IMPORTED GLOBAL)
set_target_properties(liboberon PROPERTIES IMPORTED_LOCATION
  ${CMAKE_CURRENT_LIST_DIR}/lib/cortex-m4/hard-float/liboberon_3.0.19.a
)

add_library(liboberon_mbedtls STATIC IMPORTED GLOBAL)
set_target_properties(liboberon_mbedtls PROPERTIES IMPORTED_LOCATION
  ${CMAKE_CURRENT_LIST_DIR}/lib/cortex-m4/hard-float/liboberon_mbedtls_3.0.19.a
)

target_link_libraries(app PUBLIC
  liboberon
  liboberon_mbedtls
)
