describe('Send transactions from bitcoin hotwallets', () => {
    it('Fiddle with the details of the send_dialog', () => {
        cy.viewport(1200,660)
        cy.visit('/')
        // empty so far
        cy.contains("Test Hot Wallet 1").click()
        cy.get('#btn_send').click()
        cy.get('#send_new').click()
        cy.get('#address_0').type("muuuuh")
        cy.get('#create_psbt_btn').click()
        cy.get('#messages > message-box').contains("Please provide a valid address")
        cy.get('#address_0').clear()
        cy.get('#create_psbt_btn').click()
        cy.get('#messages').contains("You provided no address")
        cy.get('#address_0').type("bcrt1qsj30deg0fgzckvlrn5757yk55yajqv6dqx0x7u")
        cy.get('#create_psbt_btn').click()
        cy.get('#messages').contains("Amount is zero")
        cy.get('#label_0').type("Burn address")
        cy.get('#amount_0').type("0.0010")
        cy.get('#toggle_advanced').click()
        cy.get('#create_psbt_btn').click()
        // 
        // cy.get('body').contains("Paste signed transaction")
        // // Some checks here
        // cy.get('#deletepsbt_btn').click()

    })
})