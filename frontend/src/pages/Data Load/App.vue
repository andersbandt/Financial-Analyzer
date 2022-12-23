
<script setup>
import 'bootstrap/dist/css/bootstrap.min.css'
import '@coreui/coreui/dist/css/coreui.min.css'
import { CCard } from '@coreui/vue'
import { CNav } from '@coreui/vue'
import { CNavItem } from '@coreui/vue';
import { CCardHeader } from '@coreui/vue';
import { CNavLink } from '@coreui/vue';
import { CCardBody } from '@coreui/vue';
import { CCardTitle } from '@coreui/vue';
import { CButton } from '@coreui/vue';
import { CCardText } from '@coreui/vue';
import { CContainer } from '@coreui/vue'
</script>

<template>
<CContainer fluid style="width: 100%; height: 100%">
<CCard class="text-center" style="width: 100%; height: 100%">
  <CCardHeader>
    <CNav variant="pills" class="card-header-pills">
      <CNavItem>
        <CNavLink
          href="#"
          active
        >
          Active
        </CNavLink>
      </CNavItem>
      <CNavItem>
        <CNavLink
          href="#"
        >
          Link
        </CNavLink>
      </CNavItem>
      <CNavItem>
        <CNavLink
          href="#"
          disabled
        >
          Disabled
        </CNavLink>
      </CNavItem>
    </CNav>
  </CCardHeader>
  <CCardBody>
    <CCardTitle>Special title treatment</CCardTitle>
    <CCardText>With supporting text below as a natural lead-in to additional content.</CCardText>
    <CButton href="#">Go somewhere</CButton>
  </CCardBody>
</CCard>
</CContainer>



</template>